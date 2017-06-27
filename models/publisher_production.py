# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Production(models.Model):
    _name = 'publisher.production'
    _order = 'name'

    name = fields.Char(string='Name', index=True, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('archived', 'Archived')
        ], string='State', default='draft', required=True)
    production_type_id = fields.Many2one('publisher.production.type', string='Production Type', required=True)
    date_start = fields.Date(string='Publication Date / Event')
    date_end = fields.Date(string='End Date')
    date_full_equipment_received = fields.Date(string='Full Equipment Received Date')
    sale_line_ids = fields.One2many('sale.order.line', 'production_id', string='Production Lines')
    expected_turnover = fields.Integer(string="Expected Turnover")
    invoicing_mode = fields.Selection([
        ('before', 'Before Publication'),
        ('after', 'After Publication'),
        ('both', 'Before & After Publication')
        ], string='Invoicing Mode', default='before', required=True)
    down_payment = fields.Float(string='Down Payment', default=0)

    @api.one
    def _compute_sale_lines_count(self):
        self.sale_lines_count = len(self.sale_line_ids)

    sale_lines_count = fields.Integer(string="Production Lines Count", compute=_compute_sale_lines_count)

    @api.one
    def _compute_sale_lines_confirmed_count(self):
        self.sale_lines_confirmed_count = 0
        for line in self.sale_line_ids:
            if line.order_id.state in ['sale', 'done']:
                self.sale_lines_confirmed_count += 1

    sale_lines_confirmed_count = fields.Integer(string="Production Lines Count", compute=_compute_sale_lines_confirmed_count)

    @api.one
    def _compute_sale_lines_full_equipment_count(self):
        self.sale_lines_full_equipment_count = 0
        for line in self.sale_line_ids:
            if line.full_equipment_received:
                self.sale_lines_full_equipment_count += 1

    sale_lines_full_equipment_count = fields.Integer(string="Production Lines Count", compute=_compute_sale_lines_full_equipment_count)

    @api.one
    def _compute_actual_turnover(self):
        # Warning: if the related sale's total price is manually changed this sum is not accurate
        self.actual_turnover = sum([line.price_subtotal for line in self.sale_line_ids])

    actual_turnover = fields.Integer(string="Actual Turnover", compute=_compute_actual_turnover)

    @api.one
    def _compute_turnover_delta(self):
        # Warning: if the related sale's total price is manually changed this calculation is not accurate
        self.turnover_delta = self.actual_turnover - self.expected_turnover

    turnover_delta = fields.Integer(string='Diff. Actual / Expected Turnover', compute=_compute_turnover_delta)