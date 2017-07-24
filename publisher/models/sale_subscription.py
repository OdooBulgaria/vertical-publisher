# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    partner_id = fields.Many2one('res.partner', string="Invoice Address")
    partner_customer_id = fields.Many2one('res.partner', string="Customer")