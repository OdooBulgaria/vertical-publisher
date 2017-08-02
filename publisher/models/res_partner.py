# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    agency = fields.Boolean(string="Is an Agency")

    invitation_ids = fields.Many2many('publisher.invitation', string="Invitations")

    production_line_count = fields.Integer(string="Production Line Count", compute='_compute_production_line_count')
    subscription_shipped_count = fields.Integer(string="Shipped Subscription Count", compute='_compute_subscription_shipped_count')
    
    @api.one
    def _compute_production_line_count(self):
        self.production_line_count = len(self.env['sale.order.line'].search(['&', ('production_id', '!=', False), '|', ('order_id.partner_id.id', '=', self.id), ('order_id.agency_id.id', '=', self.id)]))

    @api.one
    def _compute_subscription_shipped_count(self):
        self.subscription_shipped_count = len(self.env['sale.subscription'].search([('recurring_invoice_line_ids.partner_shipping_id.id', '=', self.id)]))