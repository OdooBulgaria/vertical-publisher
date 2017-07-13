# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Invitation(models.Model):
    _name = 'publisher.invitation'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)