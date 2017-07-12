# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    agency = fields.Boolean(string="Is an Agency")

    toolbox = fields.Boolean(string="Toolbox / Guide")
    fed = fields.Boolean(string="FED Invitation")
    fleet_dating = fields.Boolean(string="Fleet Dating Invitation")
    footy = fields.Boolean(string="Fleet Owner Of The Year Invit.")
    fi_awards = fields.Boolean(string="Fleet Innovation Awards Invit.")
    awards_be = fields.Boolean(string="Awards (BE) Invitation")
    network = fields.Boolean(string="Network Invitation")
    l2ffa = fields.Boolean(string="LFFA (LU) Invitation")
    experts_table = fields.Boolean(string="Experts Table Invitation")
    test_drive = fields.Boolean(string="Test Drive Invitation")
    fleet_dealer = fields.Boolean(string="Fleet Dealer")
    newsletter = fields.Boolean(string="Newsletter Marketing Subscrib.")

    production_line_count = fields.Integer(string="Production Line Count", compute='_compute_production_line_count')
    
    @api.one
    def _compute_production_line_count(self):
        self.production_line_count = len(self.env['sale.order.line'].search(['&', ('production_id', '!=', False), ('order_id.partner_id.id', '=', self.id)]))