# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AdrocShipmentTemplate(models.Model):
    _name = 'adroc.shipment.template'
    _description = 'Plantilla de Embarque'
    _order = 'name'

    # === IDENTIFICACIÓN ===
    name = fields.Char(
        string='Nombre de Plantilla',
        required=True
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

    # === CAMPOS DE SOCIOS (del base) ===
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente'
    )
    importer_exporter_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Importador/Exportador',
        domain="[('is_importer_exporter', '=', True), ('state', '=', 'approved')]"
    )
    freight_agency_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Agencia de Carga',
        domain="[('is_freight_agency', '=', True), ('state', '=', 'approved')]"
    )
    carrier_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Naviera/Aerolínea',
        domain="[('is_carrier', '=', True), ('state', '=', 'approved')]"
    )
    customs_agency_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Agencia Aduanal',
        domain="[('is_customs_agency', '=', True), ('state', '=', 'approved')]"
    )
    customs_broker_person_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Gestor Aduanero',
        domain="[('is_custom_broker_person', '=', True), ('state', '=', 'approved')]"
    )
    good_carrier_id = fields.Many2one(
        'mrdc.shipment.partner',
        string='Transportista de Mercancías',
        domain="[('is_good_carrier', '=', True), ('state', '=', 'approved')]"
    )

    # === CAMPOS DE TRANSPORTE ===
    transport_type = fields.Selection([
        ('air', 'Aéreo'),
        ('sea', 'Marítimo'),
        ('land', 'Terrestre'),
        ('multimodal', 'Multimodal'),
    ], string='Tipo de Transporte')
    incoterm = fields.Char(
        string='Incoterm'
    )
    vessel_flight_name = fields.Char(
        string='Nombre Buque/Vuelo'
    )
    voyage_number = fields.Char(
        string='Número de Viaje'
    )

    # === CAMPOS DE MERCANCÍA ===
    goods_description = fields.Text(
        string='Descripción de Mercancías'
    )
    commercial_value_usd = fields.Monetary(
        string='Valor Comercial USD',
        currency_field='usd_currency_id'
    )
    usd_currency_id = fields.Many2one(
        'res.currency',
        string='Moneda USD',
        default=lambda self: self.env.ref('base.USD', raise_if_not_found=False)
    )
    gross_weight_kg = fields.Float(
        string='Peso Bruto (kg)'
    )
    volume_m3 = fields.Float(
        string='Volumen (m³)'
    )

    # === CAMPOS DE RUTAS ===
    origin_country_id = fields.Many2one(
        'res.country',
        string='País Origen'
    )
    origin_state_id = fields.Many2one(
        'res.country.state',
        string='Estado Origen',
        domain="[('country_id', '=', origin_country_id)]"
    )
    origin_customs_id = fields.Many2one(
        'mrdc.shipment.custom',
        string='Aduana Origen'
    )
    loading_port_airport_id = fields.Many2one(
        'mrdc.shipment.port_airport',
        string='Puerto/Aeropuerto Carga'
    )
    transshipment_port_airport_ids = fields.Many2many(
        'mrdc.shipment.port_airport',
        'adroc_template_transshipment_rel',
        'template_id',
        'port_airport_id',
        string='Puertos Transbordo'
    )
    destination_country_id = fields.Many2one(
        'res.country',
        string='País Destino'
    )
    destination_state_id = fields.Many2one(
        'res.country.state',
        string='Estado Destino',
        domain="[('country_id', '=', destination_country_id)]"
    )
    destination_customs_id = fields.Many2one(
        'mrdc.shipment.custom',
        string='Aduana Destino'
    )
    unloading_port_airport_id = fields.Many2one(
        'mrdc.shipment.port_airport',
        string='Puerto/Aeropuerto Descarga'
    )

    # === CAMPOS DE CONTACTOS ===
    freight_agency_contact_name = fields.Char(
        string='Contacto Agencia Carga'
    )
    customs_agency_contact = fields.Char(
        string='Contacto Agencia Aduanal'
    )
    ground_carrier_contact = fields.Char(
        string='Contacto Transportista Terrestre'
    )

    # === CAMPOS DE TRANSPORTE TERRESTRE ===
    vehicle_plate = fields.Char(
        string='Placa Vehículo'
    )
    driver_name = fields.Char(
        string='Nombre Conductor'
    )

    # === CAMPOS DE ESTADOS INICIALES ===
    state = fields.Selection([
        ('in_transit', 'Abierto'),
        ('delivered', 'Cerrado'),
    ], string='Estado Inicial', default='in_transit')

    importer_exporter_state = fields.Selection([
        ('preview', 'Previa'),
        ('origen', 'Origen'),
        ('transit', 'Tránsito'),
        ('destination', 'Destino'),
        ('review', 'Revisión'),
        ('cancelled', 'Cancelado'),
    ], string='Estado Importador/Exportador')

    freight_agency_state = fields.Selection([
        ('preview', 'Previa'),
        ('origen', 'Origen'),
        ('transit', 'Tránsito'),
        ('destination', 'Destino'),
        ('cancelled', 'Cancelado'),
    ], string='Estado Agencia Carga')

    carrier_state = fields.Selection([
        ('preview', 'Previa'),
        ('origen', 'Origen'),
        ('transit', 'Tránsito'),
        ('destination', 'Destino'),
        ('cancelled', 'Cancelado'),
    ], string='Estado Transportista')

    customs_agency_state = fields.Selection([
        ('preview', 'Previa'),
        ('destination', 'Destino'),
        ('review', 'Revisión'),
        ('cancelled', 'Cancelado'),
    ], string='Estado Agencia Aduanal')

    customs_broker_person_state = fields.Selection([
        ('preview', 'Previa'),
        ('destination', 'Destino'),
        ('review', 'Revisión'),
        ('cancelled', 'Cancelado'),
    ], string='Estado Gestor Aduanero')

    good_carrier_state = fields.Selection([
        ('preview', 'Previa'),
        ('destination', 'Destino'),
        ('review', 'Revisión'),
        ('cancelled', 'Cancelado'),
    ], string='Estado Transportista Mercancías')

    # === CAMPOS DE CONFIGURACIÓN ===
    property_payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Plazo de Pago'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda'
    )
    tag_ids = fields.Many2many(
        'mrdc.shipment.tag',
        'adroc_shipment_template_tag_rel',
        'template_id',
        'tag_id',
        string='Etiquetas'
    )

    # === RELACIÓN CON PLANTILLAS DE FACTURA ===
    invoice_template_ids = fields.One2many(
        'adroc.shipment.template.invoice',
        'template_id',
        string='Plantillas de Factura'
    )

    def _get_template_fields(self):
        """Retorna lista de campos que pueden copiarse desde la plantilla"""
        return [
            # Socios
            'partner_id',
            'importer_exporter_id',
            'freight_agency_id',
            'carrier_id',
            'customs_agency_id',
            'customs_broker_person_id',
            'good_carrier_id',
            # Transporte
            'transport_type',
            'incoterm',
            'vessel_flight_name',
            'voyage_number',
            # Mercancía
            'goods_description',
            'commercial_value_usd',
            'gross_weight_kg',
            'volume_m3',
            # Rutas
            'origin_country_id',
            'origin_state_id',
            'origin_customs_id',
            'loading_port_airport_id',
            'transshipment_port_airport_ids',
            'destination_country_id',
            'destination_state_id',
            'destination_customs_id',
            'unloading_port_airport_id',
            # Contactos
            'freight_agency_contact_name',
            'customs_agency_contact',
            'ground_carrier_contact',
            # Transporte terrestre
            'vehicle_plate',
            'driver_name',
            # Estados
            'state',
            'importer_exporter_state',
            'freight_agency_state',
            'carrier_state',
            'customs_agency_state',
            'customs_broker_person_state',
            'good_carrier_state',
            # Configuración
            'property_payment_term_id',
            'currency_id',
            'tag_ids',
        ]

    def get_shipment_values(self):
        """Retorna diccionario de valores para aplicar a un embarque"""
        self.ensure_one()
        vals = {}
        for field_name in self._get_template_fields():
            field = self._fields.get(field_name)
            if field:
                value = getattr(self, field_name)
                if value:
                    if field.type == 'many2one':
                        vals[field_name] = value.id
                    elif field.type == 'many2many':
                        vals[field_name] = [(6, 0, value.ids)]
                    else:
                        vals[field_name] = value
        return vals

    def get_preview_text(self):
        """Genera texto de vista previa para el wizard"""
        self.ensure_one()
        lines = []

        # Información de embarque
        lines.append("INFORMACIÓN DE EMBARQUE:")
        if self.partner_id:
            lines.append(f"  - Cliente: {self.partner_id.name}")
        if self.importer_exporter_id:
            lines.append(f"  - Importador/Exportador: {self.importer_exporter_id.name}")
        if self.freight_agency_id:
            lines.append(f"  - Agencia de Carga: {self.freight_agency_id.name}")
        if self.carrier_id:
            lines.append(f"  - Naviera/Aerolínea: {self.carrier_id.name}")
        if self.customs_agency_id:
            lines.append(f"  - Agencia Aduanal: {self.customs_agency_id.name}")
        if self.customs_broker_person_id:
            lines.append(f"  - Gestor Aduanero: {self.customs_broker_person_id.name}")
        if self.good_carrier_id:
            lines.append(f"  - Transportista: {self.good_carrier_id.name}")
        if self.transport_type:
            transport_labels = dict(self._fields['transport_type'].selection)
            lines.append(f"  - Tipo Transporte: {transport_labels.get(self.transport_type, self.transport_type)}")
        if self.incoterm:
            lines.append(f"  - Incoterm: {self.incoterm}")
        if self.origin_country_id:
            lines.append(f"  - País Origen: {self.origin_country_id.name}")
        if self.destination_country_id:
            lines.append(f"  - País Destino: {self.destination_country_id.name}")
        if self.destination_customs_id:
            lines.append(f"  - Aduana Destino: {self.destination_customs_id.name}")

        # Facturas cliente
        customer_invoices = self.invoice_template_ids.filtered(lambda i: i.invoice_type == 'customer')
        if customer_invoices:
            lines.append("")
            lines.append(f"FACTURAS CLIENTE ({len(customer_invoices)}):")
            for idx, inv in enumerate(customer_invoices, 1):
                partner_name = inv.partner_id.name if inv.partner_id else 'Sin definir'
                lines.append(f"  - Factura {idx}: {partner_name}")

        # Facturas proveedor
        supplier_invoices = self.invoice_template_ids.filtered(lambda i: i.invoice_type == 'supplier')
        if supplier_invoices:
            lines.append("")
            lines.append(f"FACTURAS PROVEEDOR ({len(supplier_invoices)}):")
            for idx, inv in enumerate(supplier_invoices, 1):
                partner_name = inv.partner_id.name if inv.partner_id else 'Sin definir'
                lines.append(f"  - Factura {idx}: {partner_name}")

        return '\n'.join(lines) if lines else 'Sin datos configurados'
