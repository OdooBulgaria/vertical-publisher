# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProductionWizard(models.Model):
    _name = 'publisher.production.wizard'

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")

    def action_report(self):
        return self.env['report'].get_action(self, 'publisher.report_production_global_template', data={'date_from': self.date_from, 'date_to': self.date_to})


class ProductionGlobalReport(models.AbstractModel):
    _name = 'report.publisher.report_production_global_template'

    @api.model
    def render_html(self, docids, data=None):
        productions = self.env['publisher.production'].search(['&', ('date_closing', '>=', data['date_from']), ('date_closing', '<=', data['date_to'])])
        production_types_map = {}

        for production in productions:
            if not production.production_type_id.id in production_types_map:
                production_types_map[production.production_type_id.id] = {
                    'obj': production.production_type_id,
                    'prods': []
                }

            production_types_map[production.production_type_id.id]['prods'].append(production)

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_production_global_template')

        def render_date(date):
            date = date.split('-')
            return date[2] + '/' + date[1] + '/' + date[0]

        return report_obj.render('publisher.report_production_global_template', {
            'header_title1': _("Productions Global Status"),
            'header_title2': _("To be closed from") + " " + date_from + " " + _("to") + " " + date_to,
            'doc_ids': None,
            'doc_model': report.model,
            'docs': None,
            'date_from': render_date(data['date_from']),
            'date_to': render_date(data['date_to']),
            'data': production_types_map
        })