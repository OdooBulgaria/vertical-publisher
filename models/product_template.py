# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    format_needed = fields.Boolean(string="Format Needed")
    location_needed = fields.Boolean(string="Location Needed")
    date_start_needed = fields.Boolean(string="Publication Date Needed")
    date_end_needed = fields.Boolean(string="End Date Needed")