# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Media(models.Model):
    _name = 'publisher.media'
    _order = 'name'

    name = fields.Char(string='Name', copy=False, index=True, required=True)