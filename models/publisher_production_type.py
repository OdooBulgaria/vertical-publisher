# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProductionType(models.Model):
    _name = 'publisher.production.type'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)
    product_category_id = fields.Many2one('product.category', string='Product Category', required=True)
    media_id = fields.Many2one('publisher.media', string='Media', required=True)
    website = fields.Boolean(string='Website', required=True)
    invoicing_mode = fields.Selection([
        ('before', 'Before Publication'),
        ('after', 'After Publication'),
        ('both', 'Before & After Publication')
        ], string='Invoicing Mode', default='before', required=True)
    down_payment = fields.Float(string='Down Payment', default=0)