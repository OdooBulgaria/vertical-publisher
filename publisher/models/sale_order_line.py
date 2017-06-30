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
    date_start = fields.Date(string='Publication Date')
    date_end = fields.Date(string='End Date')
    full_equipment_received = fields.Boolean(string='Full Equipment Received')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")

    format_needed = fields.Boolean(related='production_id.production_type_id.media_id.format_needed', string="Format Needed")
    location_needed = fields.Boolean(related='production_id.production_type_id.media_id.location_needed', string="Location Needed")
    color_needed = fields.Boolean(related='production_id.production_type_id.media_id.color_needed', string="Color Needed")
    date_start_needed = fields.Boolean(related='production_id.production_type_id.media_id.date_start_needed', string="Publication Date Needed")
    date_end_needed = fields.Boolean(related='production_id.production_type_id.media_id.date_end_needed', string="End Date Needed")

    media_id = fields.Many2one(related='production_id.production_type_id.media_id', string="Media")

    # @api.one
    # def toggle_full_equipment_received(self):
    #     self.full_equipment_received = not self.full_equipment_received