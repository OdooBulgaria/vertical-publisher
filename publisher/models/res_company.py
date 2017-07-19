# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    reports_logo = fields.Binary(string="Reports Logo")
    sfc = fields.Html(string="Standard Form Contract")
    bank = fields.Char(string="BANK")
    iban = fields.Char(string="IBAN")
    bic = fields.Char(string="BIC")