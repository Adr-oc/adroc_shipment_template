# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AdrocLoadTemplateWizard(models.TransientModel):
    _name = 'adroc.load.template.wizard'
    _description = 'Wizard para Cargar Plantilla'

    shipment_id = fields.Many2one(
        'mrdc.shipment',
        string='Embarque',
        required=True,
        readonly=True
    )
    template_id = fields.Many2one(
        'adroc.shipment.template',
        string='Plantilla',
        required=True,
        domain="[('active', '=', True)]"
    )
    load_mode = fields.Selection([
        ('all', 'Cargar Todo'),
        ('shipment_only', 'Solo Información de Embarque'),
        ('customer_invoice', 'Solo Facturas Cliente'),
        ('supplier_invoice', 'Solo Facturas Proveedor'),
    ], string='Modo de Carga', required=True, default='all')

    preview_text = fields.Text(
        string='Vista Previa',
        compute='_compute_preview_text'
    )

    @api.depends('template_id', 'load_mode')
    def _compute_preview_text(self):
        for wizard in self:
            if wizard.template_id:
                lines = []
                template = wizard.template_id

                # Mostrar según el modo
                if wizard.load_mode in ('all', 'shipment_only'):
                    lines.append("INFORMACIÓN DE EMBARQUE:")
                    if template.partner_id:
                        lines.append(f"  - Cliente: {template.partner_id.name}")
                    if template.importer_exporter_id:
                        lines.append(f"  - Importador/Exportador: {template.importer_exporter_id.name}")
                    if template.freight_agency_id:
                        lines.append(f"  - Agencia de Carga: {template.freight_agency_id.name}")
                    if template.carrier_id:
                        lines.append(f"  - Naviera/Aerolínea: {template.carrier_id.name}")
                    if template.customs_agency_id:
                        lines.append(f"  - Agencia Aduanal: {template.customs_agency_id.name}")
                    if template.customs_broker_person_id:
                        lines.append(f"  - Gestor Aduanero: {template.customs_broker_person_id.name}")
                    if template.good_carrier_id:
                        lines.append(f"  - Transportista: {template.good_carrier_id.name}")
                    if template.transport_type:
                        transport_labels = {
                            'air': 'Aéreo',
                            'sea': 'Marítimo',
                            'land': 'Terrestre',
                            'multimodal': 'Multimodal'
                        }
                        lines.append(f"  - Tipo Transporte: {transport_labels.get(template.transport_type, template.transport_type)}")
                    if template.incoterm:
                        lines.append(f"  - Incoterm: {template.incoterm}")
                    if template.origin_country_id:
                        lines.append(f"  - País Origen: {template.origin_country_id.name}")
                    if template.destination_country_id:
                        lines.append(f"  - País Destino: {template.destination_country_id.name}")
                    if template.destination_customs_id:
                        lines.append(f"  - Aduana Destino: {template.destination_customs_id.name}")
                    if template.goods_description:
                        lines.append(f"  - Mercancía: {template.goods_description[:50]}...")
                    if template.gross_weight_kg:
                        lines.append(f"  - Peso: {template.gross_weight_kg} kg")
                    if template.volume_m3:
                        lines.append(f"  - Volumen: {template.volume_m3} m³")

                # Facturas cliente
                if wizard.load_mode in ('all', 'customer_invoice'):
                    customer_invoices = template.invoice_template_ids.filtered(
                        lambda i: i.invoice_type == 'customer'
                    )
                    if customer_invoices:
                        lines.append("")
                        lines.append(f"FACTURAS CLIENTE ({len(customer_invoices)}):")
                        for idx, inv in enumerate(customer_invoices, 1):
                            partner_name = inv.partner_id.name if inv.partner_id else 'Sin definir'
                            doc_type = dict(inv._fields['document_type'].selection).get(
                                inv.document_type, inv.document_type or ''
                            )
                            line_count = len(inv.line_ids)
                            lines.append(f"  - {inv.name or f'Factura {idx}'}: {partner_name} ({doc_type}) - {line_count} líneas")

                # Facturas proveedor
                if wizard.load_mode in ('all', 'supplier_invoice'):
                    supplier_invoices = template.invoice_template_ids.filtered(
                        lambda i: i.invoice_type == 'supplier'
                    )
                    if supplier_invoices:
                        lines.append("")
                        lines.append(f"FACTURAS PROVEEDOR ({len(supplier_invoices)}):")
                        for idx, inv in enumerate(supplier_invoices, 1):
                            partner_name = inv.partner_id.name if inv.partner_id else 'Sin definir'
                            doc_type = dict(inv._fields['document_type'].selection).get(
                                inv.document_type, inv.document_type or ''
                            )
                            line_count = len(inv.line_ids)
                            lines.append(f"  - {inv.name or f'Factura {idx}'}: {partner_name} ({doc_type}) - {line_count} líneas")

                wizard.preview_text = '\n'.join(lines) if lines else 'Sin datos configurados en la plantilla'
            else:
                wizard.preview_text = 'Seleccione una plantilla para ver la vista previa'

    def action_load_template(self):
        """Ejecuta la carga de la plantilla según el modo seleccionado"""
        self.ensure_one()

        if not self.template_id:
            raise UserError(_('Debe seleccionar una plantilla'))

        result_messages = []

        # Cargar información de embarque
        if self.load_mode in ('all', 'shipment_only'):
            self._load_shipment_data()
            result_messages.append('Información de embarque cargada')

        # Cargar facturas cliente
        if self.load_mode in ('all', 'customer_invoice'):
            count = self._load_customer_invoices()
            if count:
                result_messages.append(f'{count} factura(s) cliente creada(s)')

        # Cargar facturas proveedor
        if self.load_mode in ('all', 'supplier_invoice'):
            count = self._load_supplier_invoices()
            if count:
                result_messages.append(f'{count} factura(s) proveedor creada(s)')

        # Mostrar mensaje de resultado
        message = ' | '.join(result_messages) if result_messages else 'No se realizaron cambios'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Plantilla Cargada'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def _load_shipment_data(self):
        """Carga los datos de la plantilla al embarque"""
        vals = self.template_id.get_shipment_values()
        if vals:
            self.shipment_id.write(vals)

    def _load_customer_invoices(self):
        """Crea cuentas ajenas de cliente desde las plantillas"""
        customer_templates = self.template_id.invoice_template_ids.filtered(
            lambda i: i.invoice_type == 'customer'
        )
        count = 0
        for template in customer_templates:
            vals = template.get_external_account_values(self.shipment_id)
            lines = template.get_line_values()
            if lines:
                vals['line_ids'] = lines
            self.env['mrdc.external_account'].create(vals)
            count += 1
        return count

    def _load_supplier_invoices(self):
        """Crea cuentas ajenas de proveedor desde las plantillas"""
        supplier_templates = self.template_id.invoice_template_ids.filtered(
            lambda i: i.invoice_type == 'supplier'
        )
        count = 0
        for template in supplier_templates:
            vals = template.get_external_account_values(self.shipment_id)
            lines = template.get_line_values()
            if lines:
                vals['line_ids'] = lines
            self.env['mrdc.external_account'].create(vals)
            count += 1
        return count
