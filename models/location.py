# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Location(models.Model):
    _name = 'publisher.location'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)