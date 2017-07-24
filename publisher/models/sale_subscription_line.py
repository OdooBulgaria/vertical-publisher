# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    partner_shipping_id = fields.Many2one('res.partner', string="Shipping Address")
    language_id = fields.Many2one('publisher.language', string="Language")