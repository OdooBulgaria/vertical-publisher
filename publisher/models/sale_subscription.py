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
            _('Customer : ')+self.partner_customer_id.name if self.partner_customer_id else '',
            _('Shipping Address : ')+', '.join(filter(None, [
                line.partner_shipping_id.name or '',
                line.partner_shipping_id.street or '',
                line.partner_shipping_id.street2 or '',
                line.partner_shipping_id.city or '',
                line.partner_shipping_id.state_id.name or '',
                line.partner_shipping_id.zip or '',
                line.partner_shipping_id.country_id.name or '',
            ])) if line.partner_shipping_id else '',
            _('Subscription Reference : ')+self.name,
            _('Language : ')+line.language_id.name if line.language_id else '',
            _('Unit Price : ')+str(line.price_unit)+self.currency_id.symbol if line.quantity != 1 else '',
            _('Quantity : ')+str(line.quantity) if line.quantity != 1 else '',
            _('Price : ')+str(line.quantity*line.price_unit)+self.currency_id.symbol+(' - '+str(line.discount)+_(' % customer discount') if line.discount>0 else ''),
        ]))

        return vals

    @api.multi
    def set_open(self):
        return self.write({'state': 'open'})

    @api.multi
    def set_close(self):
        return self.write({'state': 'close'})