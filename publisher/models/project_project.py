# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    production_id = fields.Many2one('publisher.production', string="Production")

    def project_project_production_action(self):
        return {
            'name': ('Production'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'publisher.production',
            'type': 'ir.actions.act_window',
            'res_id': self.production_id.id
        }