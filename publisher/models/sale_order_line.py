# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    production_id = fields.Many2one('publisher.production', string="Production")
    format_id = fields.Many2one('publisher.format', string="Format")
    location_id = fields.Many2one('publisher.location', string="Location")
    color_id = fields.Many2one('publisher.color', string="Color")
    date_start = fields.Date(string='Publication Date')
    date_end = fields.Date(string='End Date')
    full_equipment_received = fields.Boolean(string='Full Equipment Received')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    attachment_count = fields.Integer(string="Attachment Count", compute='_compute_attachment_count')
    sequence_computed = fields.Integer(string="Sequence Order", compute='_compute_sequence_computed')

    format_needed = fields.Boolean(related='production_id.production_type_id.media_id.format_needed', string="Format Needed")
    location_needed = fields.Boolean(related='production_id.production_type_id.media_id.location_needed', string="Location Needed")
    color_needed = fields.Boolean(related='production_id.production_type_id.media_id.color_needed', string="Color Needed")
    date_start_needed = fields.Boolean(related='production_id.production_type_id.media_id.date_start_needed', string="Publication Date Needed")
    date_end_needed = fields.Boolean(related='production_id.production_type_id.media_id.date_end_needed', string="End Date Needed")

    media_id = fields.Many2one(related='production_id.production_type_id.media_id', string="Media")

    discount_base = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
    commission = fields.Float(string='Agency Commission (%)', digits=dp.get_precision('Discount'), default=0.0)
    discount = fields.Float(string='Total Discount (%)', digits=dp.get_precision('Discount'), default=0.0, compute='_compute_discount')

    prod_state = fields.Selection(related='production_id.state', string="Production State")


    @api.one
    @api.depends('discount_base', 'commission')
    def _compute_discount(self):
        self.discount = (1.0 - (100.0-self.discount_base)/100.0 * (100.0-self.commission)/100.0) * 100.0

    def _check_location_unique(self, vals):

        production_id = (vals.get('production_id') and self.env['publisher.production'].search([('id', '=', vals['production_id'])])) or self.production_id or False
        location_id = (vals.get('location_id') and self.env['publisher.location'].search([('id', '=', vals['location_id'])])) or self.location_id or False
        name = vals.get('name') or self.name or False

        if production_id and location_id and location_id.unique:
            for line in production_id.sale_line_ids:
                if line.id != self.id:
                    if location_id.id == line.location_id.id:
                        raise exceptions.ValidationError(_('Line ') + name + _(' : Another line (') + line.order_id.name + ' - ' + line.name + _(') in the production (') + production_id.name + _(') has the same location which is set as unique.'))
                        return False

        return True

    @api.model
    def create(self, vals):
        if not self._check_location_unique(vals):
            return False

        return super(SaleOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if not self._check_location_unique(vals):
            return False

        if self.production_id:
            if 'full_equipment_received' in vals:
                self.production_id.message_post(subject=self.name, body=self.name + " : " + (_("Full equipment is received") if vals['full_equipment_received'] else _("Equipment set as not received")))
            if 'attachment_ids' in vals:
                delta = len(vals['attachment_ids'][0][2]) - len(self.attachment_ids)
                self.production_id.message_post(subject=self.name, body=self.name + " : " + str(abs(delta)) + " " + (_(" attachment(s) added") if delta>0 else _(" attachment(s) deleted")))
        return super(SaleOrderLine, self).write(vals)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.format_id = self.product_id.format_id
            self.location_id = self.product_id.location_id
            self.color_id = self.product_id.color_id
        else:
            self.format_id = False
            self.location_id = False
            self.color_id = False

    @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        self.discount_base = 0.0
        if not (self.product_id and self.product_uom and
                self.order_id.partner_id and self.order_id.pricelist_id and
                self.order_id.pricelist_id.discount_policy == 'without_discount' and
                self.env.user.has_group('sale.group_discount_per_so_line')):
            return

        context_partner = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order)
        pricelist_context = dict(context_partner, uom=self.product_uom.id)

        price, rule_id = self.order_id.pricelist_id.with_context(pricelist_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        new_list_price, currency_id = self.with_context(context_partner)._get_real_price_currency(self.product_id, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
        new_list_price = self.env['account.tax']._fix_tax_included_price(new_list_price, self.product_id.taxes_id, self.tax_id)

        if new_list_price != 0:
            if self.product_id.company_id and self.order_id.pricelist_id.currency_id != self.product_id.company_id.currency_id:
                # new_list_price is in company's currency while price in pricelist currency
                new_list_price = self.env['res.currency'].browse(currency_id).with_context(context_partner).compute(new_list_price, self.order_id.pricelist_id.currency_id)
            discount_base = (new_list_price - price) / new_list_price * 100
            if discount_base > 0:
                self.discount_base = discount_base

    @api.one
    def _compute_sequence_computed(self):
        self.sequence_computed = 1
        for line in self.order_id.order_line:
            if line.id == self.id:
                break
            self.sequence_computed += 1

    @api.one
    def _compute_attachment_count(self):
        self.attachment_count = len(self.attachment_ids)

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)

        vals['name'] = '\n'.join(filter(None, [
            self.name,
            _('Unit Price : ')+str(self.price_unit)+self.currency_id.symbol if self.product_uom_qty != 1 or qty != self.product_uom_qty else '',
            _('Quantity : ')+str(self.product_uom_qty) if self.product_uom_qty != 1 else '',
            _('Invoiced Percentage : ')+str(round(qty / self.product_uom_qty * 100, 2))+' %' if qty != self.product_uom_qty else '',
            _('Your Customer : ')+self.order_id.partner_id.name if self.order_id.partner_invoice_id else '',
            _('Price : ')+str(qty*self.price_unit)+self.currency_id.symbol+(' - '+str(self.discount_base)+_(' % customer discount') if self.discount_base>0 else '')+(' = '+str(qty*self.price_unit*(1-self.discount_base/100))+self.currency_id.symbol if self.discount_base>0 and self.commission>0 else '')+(' - '+str(self.commission)+_(' % agency commission') if self.commission>0 else ''),
        ]))

        return vals

    # @api.one
    # def toggle_full_equipment_received(self):
    #     self.full_equipment_received = not self.full_equipment_received