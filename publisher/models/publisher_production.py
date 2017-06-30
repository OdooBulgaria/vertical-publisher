# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

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
    actual_turnover = fields.Monetary(string="Actual Turnover", compute='_compute_actual_turnover')
    turnover_delta = fields.Monetary(string='Diff. Actual / Expected Turnover', compute='_compute_turnover_delta')
    turnover_delta_sign = fields.Char(string='Turnover Delta Sign', compute='_compute_turnover_delta_sign')

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
    def _compute_actual_turnover(self):
        # Warning: if the related sale's total price is manually changed this sum is not accurate
        self.actual_turnover = sum([line.price_subtotal for line in self.sale_line_ids])


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