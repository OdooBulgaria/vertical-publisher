# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from itertools import groupby

import logging
_logger = logging.getLogger(__name__)
import tempfile
import zipfile
import base64
import urllib

class Production(models.Model):
    _name = 'publisher.production'
    _order = 'name'

    name = fields.Char(string='Name', index=True, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('archived', 'Archived')
        ], string='State', default='draft', required=True)
    production_type_id = fields.Many2one('publisher.production.type', string='Production Type', required=True)
    project_id = fields.Many2one('project.project', string="Project");
    date_start = fields.Date(string='Publication Date / Event')
    date_end = fields.Date(string='End Date')
    date_full_equipment_limit = fields.Date(string='Full Equipment Limit Date')
    sale_line_ids = fields.One2many('sale.order.line', 'production_id', string='Production Lines')
    expected_turnover = fields.Monetary(string="Expected Turnover")
    invoicing_mode = fields.Selection([
        ('before', 'Before Publication'),
        ('after', 'After Publication'),
        ('both', 'Before & After Publication')
        ], string='Invoicing Mode', default='before', required=True)
    down_payment = fields.Float(string='Down Payment', default=0)

    # sale_lines_count = fields.Integer(string="Production Lines Count", compute=_compute_sale_lines_count)
    sale_lines_confirmed_count = fields.Char(string="Confirmed Lines", compute='_compute_sale_lines_confirmed_count')
    sale_lines_full_equipment_count = fields.Char(string="Equip. Received Lines", compute='_compute_sale_lines_full_equipment_count')
    potential_turnover = fields.Monetary(string="Potential Turnover", compute='_compute_potential_turnover')
    actual_turnover = fields.Monetary(string="Actual Turnover", compute='_compute_actual_turnover')
    turnover_delta = fields.Monetary(string='Diff. Actual / Expected Turnover', compute='_compute_turnover_delta')
    turnover_delta_sign = fields.Char(string='Turnover Delta Sign', compute='_compute_turnover_delta_sign')

    export_file = fields.Binary(attachment=True, help="This field holds the export file for Sage 50.", readonly=True)

    # @api.one
    # def _compute_sale_lines_count(self):
    #     self.sale_lines_count = len(self.sale_line_ids)


    @api.one
    def _compute_sale_lines_confirmed_count(self):
        count = 0
        for line in self.sale_line_ids:
            if line.order_id.state in ['sale', 'done']:
                count += 1

        self.sale_lines_confirmed_count = str(count) + '/' + str(len(self.sale_line_ids))


    @api.one
    def _compute_sale_lines_full_equipment_count(self):
        count = 0
        for line in self.sale_line_ids:
            if line.full_equipment_received:
                count += 1

        self.sale_lines_full_equipment_count = str(count) + '/' + str(len(self.sale_line_ids))


    @api.one
    def _compute_potential_turnover(self):
        self.potential_turnover = sum([line.price_subtotal for line in self.sale_line_ids])


    @api.one
    def _compute_actual_turnover(self):
        self.actual_turnover = 0
        for line in self.sale_line_ids:
            if line.order_id.state in ['sale', 'done']:
                self.actual_turnover += line.price_subtotal


    @api.depends('expected_turnover')
    @api.one
    def _compute_turnover_delta(self):
        self.turnover_delta = self.actual_turnover - self.expected_turnover


    @api.depends('expected_turnover')
    @api.one
    def _compute_turnover_delta_sign(self):
        self.turnover_delta_sign = '+' if self.turnover_delta >= 0 else ''

    @api.one
    def action_create_project(self):
        self.project_id = self.env['project.project'].create({
            'name': self.name, 'production_id': self.id
        })

    @api.multi
    @api.onchange('production_type_id')
    def onchange_production_type_id(self):
        for production in self:
            production.invoicing_mode = production.production_type_id.invoicing_mode
            production.down_payment = production.production_type_id.down_payment

    @api.multi
    def order_lines_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.sale_line_ids, lambda l: l.layout_category_id):
            # If last added category induced a pagebreak, this one will be on a new page
            if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
                report_pages.append([])
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or 'Uncategorized',
                'subtotal': category and category.subtotal,
                'pagebreak': category and category.pagebreak,
                'lines': list(lines)
            })

        return report_pages

    @api.multi
    def print_production(self):
        return self.env['report'].get_action(self, 'publisher.report_production')

    @api.multi
    def download_attachments(self):

        def get_valid_filename(string):
            remove_illegals_map = dict((ord(char), None) for char in '\/*?:"<>|')
            return string.translate(remove_illegals_map)

        temp_zip = tempfile.mktemp(suffix='.zip')
        temp_file = tempfile.mktemp(suffix='')
        zip_file_object = zipfile.ZipFile(temp_zip, "w")

        existing_folders = {}

        for line in self.sale_line_ids:

            base_folder_name = get_valid_filename(line.order_id.partner_id.name + " - " + line.product_id.name + " (" + line.order_id.name + " #" + str(line.sequence_computed) + ")")

            folder_name = base_folder_name
            counter = 1
            while folder_name in existing_folders:
                counter += 1
                folder_name = base_folder_name + " - " + str(counter)

            existing_folders[folder_name] = True

            for f in line.attachment_ids:
                fn = open(temp_file, 'w')
                fn.write(base64.b64decode(f.datas))
                fn.close()
                zip_file_object.write(temp_file, folder_name+"/"+f.name)

        zip_file_object.close()

        fn = open(temp_zip, 'r')
        self.export_file = base64.encodestring(fn.read())
        fn.close()

        return {
            'type' : 'ir.actions.act_url',
            'url': '/web/binary/download_document?' + urllib.urlencode({
                'model': 'publisher.production',
                'field': 'export_file',
                'id': self.id,
                'filename': get_valid_filename(self.name) + " (Attachments).zip"
            }),
            'target': 'blank',
        }