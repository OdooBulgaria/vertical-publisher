# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    production_id = fields.Many2one('publisher.production', string="Production")
    format_id = fields.Many2one('publisher.format', string="Format")
    location_id = fields.Many2one('publisher.location', string="Location")
    color_id = fields.Many2one('publisher.color', string="Color")
    commission = fields.Float(string="Commission")
    website = fields.Char(string="Website")
    date_start = fields.Date(string='Publication Date')
    date_end = fields.Date(string='End Date')
    full_equipment_received = fields.Boolean(string='Full Equipment Received')