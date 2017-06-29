# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    production_line_count = fields.Integer(string="Production Line Count", compute='_compute_production_line_count')
    
    @api.one
    def _compute_production_line_count(self):
        self.production_line_count = len(self.env['sale.order.line'].search(['&', ('production_id', '!=', False), ('product_id.product_tmpl_id.id', '=', self.id)]))