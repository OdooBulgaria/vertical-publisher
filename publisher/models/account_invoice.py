# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    client_ref = fields.Char(string='Customer Reference')



class AccountInvoiceReport(models.AbstractModel):
    _name = 'report.account.report_invoice'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('account.report_invoice')
        docargs = {
        	'header_title1_1': _("Invoice"),
            'header_title1_2': _("PRO-FORMA"),
            'header_title1_3': _("Draft Invoice"),
            'header_title1_4': _("Cancelled Invoice"),
            'header_title1_5': _("Refund"),
            'header_title1_6': _("Vendor Refund"),
            'header_title1_7': _("Vendor Bill"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['account.invoice'].search([('id', 'in', docids)])
        }

        return report_obj.render('account.report_invoice', docargs)

class AccountInvoiceDuplicateReport(models.AbstractModel):
    _name = 'report.publisher.report_invoice_publisher_duplicate'

    @api.model
    def render_html(self, docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('publisher.report_invoice_publisher_duplicate')
        docargs = {
            'header_title1_1': _("Duplicate refund"),
            'header_title1_2': _("Duplicate invoice"),
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env['account.invoice'].search([('id', 'in', docids)])
        }

        return report_obj.render('publisher.report_invoice_publisher_duplicate', docargs)