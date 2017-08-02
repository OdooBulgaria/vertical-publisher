# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    partner_id = fields.Many2one('res.partner', string="Invoice Address")
    partner_customer_id = fields.Many2one('res.partner', string="Customer")

    @api.multi
    def _prepare_invoice_line(self, line, fiscal_position):
        vals = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position)

        vals['name'] = '\n'.join(filter(None, [
            line.name,
            _('Unit Price : ')+str(line.price_unit)+line.analytic_account_id.currency_id.symbol if line.quantity != 1 else '',
            _('Quantity : ')+str(line.quantity) if line.quantity != 1 else '',
            _('Price : ')+str(line.quantity*line.price_unit)+line.analytic_account_id.currency_id.symbol+(' - '+str(line.discount)+_(' % customer discount') if line.discount>0 else ''),
        ]))

        return vals