# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class Project(models.Model):
    _inherit = 'project.project'

    production_id = fields.Many2one('publisher.production', string="Production")

    def project_project_production_action(self):
        return {
            'name': _('Production'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'publisher.production',
            'type': 'ir.actions.act_window',
            'res_id': self.production_id.id
        }

    @api.model
    def create(self, values):
        if not values.get('type_ids'):
            stage_ids = self.env['publisher.project.template'].get_project_stages([('is_default_template', '=', True)])

            if stage_ids:
                values['type_ids'] = [(4, stage_id) for stage_id in stage_ids]

        return super(Project, self).create(values)