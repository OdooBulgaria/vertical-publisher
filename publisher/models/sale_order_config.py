# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    reports_logo = fields.Binary(string="Reports Logo", default='_get_reports_logo')

    @api.one
    def _get_reports_logo(self):
    	return self.env['sale.config.settings'].search([])[-1].reports_logo