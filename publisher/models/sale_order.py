# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agency_id = fields.Many2one('res.partner', string="Agency")
    reference = fields.Char(string='Internal Reference')
    has_production = fields.Boolean(string='Has Production', compute='_compute_has_production')

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

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'publisher.report_saleorder_publisher')

    @api.multi
    def print_quotation_noprice(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'publisher.report_saleorder_publisher_noprice')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order.publisher') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.publisher') or _('New')

        return super(SaleOrder, self).create(vals)

    @api.one
    @api.depends('order_line')
    def _compute_has_production(self):
        self.has_production = False
        for line in self.order_line:
            if line.production_id:
                self.has_production = True
                break;



class SaleOrderReport(models.AbstractModel):
    _name = 'report.publisher.report_saleorder_publisher_noprice'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_saleorder_publisher')
        docargs = {
            'header_title1_1': _("Order"),
            'header_title1_2': _("Quotation"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['sale.order'].search([('id', 'in', docids)]),
            'no_price': True
        }

        return report_obj.render('publisher.report_saleorder_publisher', docargs)