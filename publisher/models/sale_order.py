# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agency_id = fields.Many2one('res.partner', string="Agency")

    @api.multi
    @api.onchange('partner_invoice_id', 'partner_id', 'agency_id')
    def onchange_partner_invoice_id(self):
        """
        Trigger the change of fiscal position when the invoice address is modified.
        """
        self.fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id, self.partner_invoice_id.id)
        return {}

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the invoice address when the partner is changed.
        """

        res = super(SaleOrder, self).onchange_partner_id()

        if self.agency_id:
            self.update({
                'partner_invoice_id': self.agency_id.address_get(['invoice'])['invoice']
            })

    @api.multi
    @api.onchange('agency_id')
    def onchange_agency_id(self):
        """
        Update the invoice address when the agency is changed.
        """

        if self.agency_id:
            addr =  self.agency_id.address_get(['invoice'])['invoice']
        elif self.partner_id:
            addr =  self.partner_id.address_get(['invoice'])['invoice']
        else:
            addr = False

        self.update({
            'partner_invoice_id': addr
        })