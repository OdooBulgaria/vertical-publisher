# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProductionWizard(models.Model):
    _name = 'publisher.production.wizard'

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")

    def action_report(self):

        report_obj = self.env['publisher.production'].search(['&', ('date_closing', '>=', self.date_from), ('date_closing', '<=', self.date_to)]).ids

        vals =  self.env['report'].get_action(self, 'publisher.report_production_global_template')

        if not vals.datas:
            vals.datas = {}

        vals.datas.ids = report_obj
        vals.datas.model = 'publisher.production'
        vals.datas.form = report_obj

        return vals

        # return {
        #     'type': 'ir.actions.report.xml',
        #     'report_name': 'publisher.report_production_global_template',
        #     'datas': {
        #         'ids': report_obj,
        #         'model': 'publisher.production',
        #         'form': report_obj,
        #     },
        # }

        # _logger.info('\n\n'+str(self.env['report'].get_action(objects, 'publisher.report_production_global_template'))+'\n\n')

        # return self.env['report'].get_action(objects, 'publisher.report_production_global_template')