# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json


class AdrocShipmentTemplate(models.Model):
    _name = 'adroc.shipment.template'
    _description = 'Plantilla de Embarque'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # === IDENTIFICACIÓN ===
    name = fields.Char(
        string='Nombre de Plantilla',
        required=True,
        tracking=True
    )
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    notes = fields.Text(
        string='Notas'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company
    )

    # === DATOS EN JSON (flexible para cualquier campo) ===
    template_data = fields.Text(
        string='Datos de Plantilla (JSON)',
        help='Datos del embarque en formato JSON'
    )

    # === CAMPO PARA MOSTRAR RESUMEN ===
    field_summary = fields.Text(
        string='Resumen de Campos',
        compute='_compute_field_summary'
    )

    field_count = fields.Integer(
        string='Campos',
        compute='_compute_field_summary'
    )

    # === RELACIÓN CON PLANTILLAS DE FACTURA ===
    invoice_template_ids = fields.One2many(
        'adroc.shipment.template.invoice',
        'template_id',
        string='Plantillas de Factura'
    )

    @api.depends('template_data')
    def _compute_field_summary(self):
        for record in self:
            if record.template_data:
                try:
                    data = json.loads(record.template_data)
                    lines = []
                    for item in data:
                        field_label = item.get('label', item.get('field', ''))
                        value = item.get('display_value', item.get('value', ''))
                        if field_label and value:
                            lines.append(f"• {field_label}: {value}")
                    record.field_summary = '\n'.join(lines) if lines else 'Sin datos'
                    record.field_count = len(data)
                except (json.JSONDecodeError, TypeError):
                    record.field_summary = 'Error al leer datos'
                    record.field_count = 0
            else:
                record.field_summary = 'Sin datos configurados'
                record.field_count = 0

    def get_shipment_values(self):
        """Retorna diccionario de valores para aplicar a un embarque"""
        self.ensure_one()
        if not self.template_data:
            return {}

        try:
            data = json.loads(self.template_data)
            shipment_model = self.env['mrdc.shipment']
            vals = {}

            for item in data:
                field_name = item.get('field')
                value = item.get('value')
                field_type = item.get('type')

                if not field_name or value is None:
                    continue

                # Verificar que el campo existe en mrdc.shipment
                if field_name not in shipment_model._fields:
                    continue

                # Convertir según el tipo
                if field_type == 'many2one':
                    # Verificar que el registro existe
                    if value:
                        vals[field_name] = value
                elif field_type == 'many2many':
                    if value and isinstance(value, list):
                        vals[field_name] = [(6, 0, value)]
                else:
                    vals[field_name] = value

            return vals
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_preview_text(self):
        """Genera texto de vista previa para el wizard"""
        self.ensure_one()
        return self.field_summary or 'Sin datos configurados'
