# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Color(models.Model):
    _name = 'publisher.color'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True)