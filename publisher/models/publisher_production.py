# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from itertools import groupby

import logging
_logger = logging.getLogger(__name__)
import tempfile
import zipfile
import base64
import urllib

import datetime

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
    date_start = fields.Date(string='Publication Date / Event', required=True)
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
    sale_ids = fields.Many2many('sale.order', string="Sales", compute='_compute_sale_ids')
    invoice_ids = fields.Many2many('account.invoice', string="Invoices", compute='_compute_invoice_ids')
    invoice_count = fields.Integer(string="Invoice Count", compute='_compute_invoice_count')

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
    def _compute_sale_ids(self):
        sale_ids_id = []
        for line in self.sale_line_ids:
            if line.order_id.id not in sale_ids_id:
                sale_ids_id.append(line.order_id.id)
        self.sale_ids = self.env['sale.order'].search([('id', 'in', sale_ids_id)])

    @api.one
    def _compute_invoice_ids(self):
        invoice_ids_id = []
        for line in self.sale_line_ids:
            for invoice_line in line.invoice_lines:
                if not invoice_line.invoice_id.id in invoice_ids_id:
                    invoice_ids_id.append(invoice_line.invoice_id.id)
        self.invoice_ids = self.env['account.invoice'].search([('id', 'in', invoice_ids_id)])

    @api.one
    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        self.invoice_count = len(self.invoice_ids)

    @api.one
    def action_create_project(self):
        self.project_id = self.env['project.project'].create({
            'name': self.name, 'production_id': self.id
        })

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

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
        return self.env['report'].get_action(self, 'publisher.report_production_template')

    @api.multi
    def print_production_invoice_status(self):
        return self.env['report'].get_action(self, 'publisher.report_production_invoice_status_template')

    @api.multi
    def download_attachments(self):
        self.ensure_one()

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



    @api.multi
    def create_invoices(self):
        self.ensure_one()

        # Extract every sale to invoice & associate lines
        sale_map = {}
        for line in self.sale_line_ids:
            if line.invoice_status == 'to invoice':
                if not line.order_id.id in sale_map:
                    sale_map[line.order_id.id] = [line]
                else:
                    sale_map[line.order_id.id].append(line)

        company_id = self.env.user.company_id
        account_journal_id = self.env['account.journal'].search([('company_id', '=', company_id.id), ('type', '=', 'sale')])[0]
        now = datetime.datetime.now()

        invoice_ids = []

        # browse every sale to invoice
        for sale_id_id in sale_map:
            
            lines = sale_map[sale_id_id]
            sale_id = lines[0].order_id
            partner_invoice_id = sale_id.partner_invoice_id

            invoice_id = False

            # browse every line to invoice
            for line in lines:

                def get_invoice_quantity(self, line):

                    def get_ratio_to_be_invoiced(self):
                        if now < datetime.datetime.strptime(self.date_start, '%Y-%m-%d'):
                            if self.invoicing_mode == 'after':
                                return False
                            elif self.invoicing_mode == 'both':
                                if self.down_payment:
                                    return self.down_payment / 100.0
                                return False
                        return 1.0

                    ratio = get_ratio_to_be_invoiced(self)

                    if not ratio:
                        return False

                    invoice_quantity = line.product_uom_qty * ratio - line.qty_invoiced

                    if invoice_quantity <= 0.0:
                        return False

                    return invoice_quantity

                quantity = get_invoice_quantity(self, line)

                # if there is something to invoice
                if quantity:

                    # if invoice does not exist yet
                    if not invoice_id:
                        invoice_id = self.env['account.invoice'].create({
                            'company_id' : company_id.id,
                            'currency_id' : self.currency_id.id,
                            'journal_id' : account_journal_id.id,
                            'partner_id' : partner_invoice_id.id,
                            'client_ref' : sale_id.client_order_ref,
                            'reference' : sale_id.reference,
                            'date_invoice' : now.strftime('%Y-%m-%d'),
                            'state' : 'draft',
                            'reference_type' : 'none',
                            'fiscal_position_id' : sale_id.fiscal_position_id.id,
                            'payment_term_id' : sale_id.payment_term_id.id,
                            'account_id' : partner_invoice_id.property_account_receivable_id.id,
                        })
                        invoice_ids.append(invoice_id.id)

                    description = '\n'.join(filter(None, [
                        line.name,
                        self.name,
                        'Format : '+line.format_id.name if line.format_id else '',
                        'Your Customer : '+sale_id.partner_id.name if sale_id.partner_invoice_id else '',
                        'Price : '+str(quantity*line.price_unit)+self.currency_id.symbol+(' - '+str(line.discount_base)+' % customer discount' if line.discount_base>0 else '')+(' = '+str(quantity*line.price_unit*(1-line.discount_base/100))+self.currency_id.symbol if line.discount_base>0 and line.commission>0 else '')+(' - '+str(line.commission)+' % agency commission' if line.commission>0 else ''),
                    ]))

                    invoice_line_id = self.env['account.invoice.line'].create({
                        'invoice_id' : invoice_id.id,
                        'product_id' : line.product_id.id,
                        'name' : description,
                        'quantity' : quantity,
                        'price_unit' : line.price_unit,
                        'discount' : line.discount,
                        'account_id' : partner_invoice_id.property_account_receivable_id.id,
                        'sale_line_ids': [(4, [line.id])]
                    })

        if not invoice_ids:
            raise exceptions.ValidationError('Not any line to invoice, make sure the sale orders are confirmed and the production publication date / invoicing mode are ok.')
            return False

        action = self.env.ref('account.action_invoice_tree1').read()[0]

        if len(invoice_ids) > 1:
            action['domain'] = [('id', 'in', invoice_ids)]
        else:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoice_ids[0]

        return action