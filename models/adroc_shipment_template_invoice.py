# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AdrocShipmentTemplateInvoice(models.Model):
    _name = 'adroc.shipment.template.invoice'
    _description = 'Plantilla de Factura de Embarque'
    _order = 'template_id, invoice_type, id'

    template_id = fields.Many2one(
        'adroc.shipment.template',
        string='Plantilla',
        required=True,
        ondelete='cascade'
    )
    name = fields.Char(
        string='Nombre/Descripción'
    )
    invoice_type = fields.Selection([
        ('customer', 'Factura Cliente (Cobrar)'),
        ('supplier', 'Factura Proveedor (Pagar)'),
    ], string='Tipo', required=True, default='customer')

    # Socios
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente/Proveedor'
    )
    partner_origin_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Socio Origen'
    )
    partner_destiny_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Socio Destino'
    )

    # Configuración
    document_type = fields.Selection([
        ('individual', 'Individual'),
        ('usd', 'Dólares'),
        ('gtq', 'Quetzales'),
        ('inverse', 'Inverso'),
    ], string='Tipo de Documento', default='individual')

    journal_id = fields.Many2one(
        'account.journal',
        string='Diario',
        domain="[('type', '=', 'sale')]"
    )

    # Tasas
    gtq_rate = fields.Float(
        string='Tasa GTQ'
    )
    usd_rate = fields.Float(
        string='Tasa USD'
    )

    # Etiquetas
    tag_ids = fields.Many2many(
        'mrdc.external_account.tag',
        'adroc_invoice_template_tag_rel',
        'invoice_template_id',
        'tag_id',
        string='Etiquetas'
    )

    # Líneas
    line_ids = fields.One2many(
        'adroc.shipment.template.invoice.line',
        'invoice_template_id',
        string='Líneas'
    )

    def get_external_account_values(self, shipment):
        """Retorna valores para crear una cuenta ajena"""
        self.ensure_one()
        move_type = 'out_invoice' if self.invoice_type == 'customer' else 'in_invoice'
        vals = {
            'shipment_id': shipment.id,
            'move_type': move_type,
        }
        if self.partner_id:
            vals['partner_id'] = self.partner_id.id
        if self.partner_origin_id:
            vals['partner_origin_id'] = self.partner_origin_id.id
        if self.partner_destiny_id:
            vals['partner_destiny_id'] = self.partner_destiny_id.id
        if self.document_type:
            vals['document_type'] = self.document_type
        if self.journal_id:
            vals['journal_id'] = self.journal_id.id
        if self.gtq_rate:
            vals['gtq_rate'] = self.gtq_rate
        if self.usd_rate:
            vals['usd_rate'] = self.usd_rate
        if self.tag_ids:
            vals['tag_ids'] = [(6, 0, self.tag_ids.ids)]
        return vals

    def get_line_values(self):
        """Retorna lista de valores para crear líneas de cuenta ajena"""
        self.ensure_one()
        lines = []
        for line in self.line_ids:
            line_vals = {}
            if line.supplier_partner_id:
                line_vals['supplier_partner_id'] = line.supplier_partner_id.id
            if line.product_id:
                line_vals['product_id'] = line.product_id.id
            if line.description:
                line_vals['ref'] = line.description
            if line.currency_id:
                line_vals['currency_id'] = line.currency_id.id
            if line.amount:
                line_vals['amount'] = line.amount
            if line_vals:
                lines.append((0, 0, line_vals))
        return lines


class AdrocShipmentTemplateInvoiceLine(models.Model):
    _name = 'adroc.shipment.template.invoice.line'
    _description = 'Línea de Plantilla de Factura'
    _order = 'invoice_template_id, id'

    invoice_template_id = fields.Many2one(
        'adroc.shipment.template.invoice',
        string='Plantilla de Factura',
        required=True,
        ondelete='cascade'
    )
    supplier_partner_id = fields.Many2one(
        'res.partner',
        string='Proveedor'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto'
    )
    description = fields.Char(
        string='Descripción'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda'
    )
    amount = fields.Monetary(
        string='Monto',
        currency_field='currency_id'
    )
