# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AdrocCreateTemplateWizard(models.TransientModel):
    _name = 'adroc.create.template.wizard'
    _description = 'Wizard para Crear Plantilla desde Embarque'

    shipment_id = fields.Many2one(
        'mrdc.shipment',
        string='Embarque',
        required=True,
        readonly=True
    )
    template_name = fields.Char(
        string='Nombre de Plantilla',
        required=True
    )
    notes = fields.Text(
        string='Notas'
    )

    # === OPCIONES DE QUÉ INCLUIR ===
    include_partners = fields.Boolean(
        string='Socios',
        default=True,
        help='Cliente, Importador/Exportador, Agencia de Carga, etc.'
    )
    include_transport = fields.Boolean(
        string='Transporte',
        default=True,
        help='Tipo de transporte, Incoterm, Buque/Vuelo, etc.'
    )
    include_goods = fields.Boolean(
        string='Mercancía',
        default=True,
        help='Descripción, Peso, Volumen, Valor Comercial'
    )
    include_routes = fields.Boolean(
        string='Rutas',
        default=True,
        help='País/Aduana Origen, País/Aduana Destino, Puertos'
    )
    include_contacts = fields.Boolean(
        string='Contactos',
        default=True,
        help='Contactos de agencias y transportistas'
    )
    include_states = fields.Boolean(
        string='Estados',
        default=False,
        help='Estados iniciales de cada entidad'
    )
    include_config = fields.Boolean(
        string='Configuración',
        default=True,
        help='Plazo de pago, Moneda, Etiquetas'
    )
    include_customer_invoices = fields.Boolean(
        string='Facturas Cliente',
        default=True,
        help='Cuentas ajenas de cliente existentes'
    )
    include_supplier_invoices = fields.Boolean(
        string='Facturas Proveedor',
        default=True,
        help='Cuentas ajenas de proveedor existentes'
    )

    preview_text = fields.Text(
        string='Vista Previa',
        compute='_compute_preview_text'
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get('active_model') == 'mrdc.shipment' and self._context.get('active_id'):
            shipment = self.env['mrdc.shipment'].browse(self._context['active_id'])
            res['shipment_id'] = shipment.id
            res['template_name'] = f"Plantilla - {shipment.name}" if shipment.name else "Nueva Plantilla"
        return res

    @api.depends('shipment_id', 'include_partners', 'include_transport', 'include_goods',
                 'include_routes', 'include_contacts', 'include_states', 'include_config',
                 'include_customer_invoices', 'include_supplier_invoices')
    def _compute_preview_text(self):
        for wizard in self:
            if not wizard.shipment_id:
                wizard.preview_text = 'No hay embarque seleccionado'
                continue

            lines = []
            shipment = wizard.shipment_id

            if wizard.include_partners:
                partner_lines = []
                if shipment.partner_id:
                    partner_lines.append(f"  - Cliente: {shipment.partner_id.name}")
                if hasattr(shipment, 'importer_exporter_id') and shipment.importer_exporter_id:
                    partner_lines.append(f"  - Importador/Exportador: {shipment.importer_exporter_id.name}")
                if hasattr(shipment, 'freight_agency_id') and shipment.freight_agency_id:
                    partner_lines.append(f"  - Agencia de Carga: {shipment.freight_agency_id.name}")
                if hasattr(shipment, 'carrier_id') and shipment.carrier_id:
                    partner_lines.append(f"  - Naviera/Aerolínea: {shipment.carrier_id.name}")
                if hasattr(shipment, 'customs_agency_id') and shipment.customs_agency_id:
                    partner_lines.append(f"  - Agencia Aduanal: {shipment.customs_agency_id.name}")
                if hasattr(shipment, 'customs_broker_person_id') and shipment.customs_broker_person_id:
                    partner_lines.append(f"  - Gestor Aduanero: {shipment.customs_broker_person_id.name}")
                if hasattr(shipment, 'good_carrier_id') and shipment.good_carrier_id:
                    partner_lines.append(f"  - Transportista: {shipment.good_carrier_id.name}")
                if partner_lines:
                    lines.append("📋 SOCIOS:")
                    lines.extend(partner_lines)

            if wizard.include_transport:
                transport_lines = []
                if hasattr(shipment, 'transport_type') and shipment.transport_type:
                    transport_labels = {'air': 'Aéreo', 'sea': 'Marítimo', 'land': 'Terrestre', 'multimodal': 'Multimodal'}
                    transport_lines.append(f"  - Tipo: {transport_labels.get(shipment.transport_type, shipment.transport_type)}")
                if hasattr(shipment, 'incoterm') and shipment.incoterm:
                    transport_lines.append(f"  - Incoterm: {shipment.incoterm}")
                if hasattr(shipment, 'vessel_flight_name') and shipment.vessel_flight_name:
                    transport_lines.append(f"  - Buque/Vuelo: {shipment.vessel_flight_name}")
                if transport_lines:
                    lines.append("")
                    lines.append("🚢 TRANSPORTE:")
                    lines.extend(transport_lines)

            if wizard.include_goods:
                goods_lines = []
                if hasattr(shipment, 'goods_description') and shipment.goods_description:
                    desc = shipment.goods_description[:50] + '...' if len(shipment.goods_description) > 50 else shipment.goods_description
                    goods_lines.append(f"  - Descripción: {desc}")
                if hasattr(shipment, 'gross_weight_kg') and shipment.gross_weight_kg:
                    goods_lines.append(f"  - Peso: {shipment.gross_weight_kg} kg")
                if hasattr(shipment, 'volume_m3') and shipment.volume_m3:
                    goods_lines.append(f"  - Volumen: {shipment.volume_m3} m³")
                if goods_lines:
                    lines.append("")
                    lines.append("📦 MERCANCÍA:")
                    lines.extend(goods_lines)

            if wizard.include_routes:
                route_lines = []
                if hasattr(shipment, 'origin_country_id') and shipment.origin_country_id:
                    route_lines.append(f"  - País Origen: {shipment.origin_country_id.name}")
                if hasattr(shipment, 'destination_country_id') and shipment.destination_country_id:
                    route_lines.append(f"  - País Destino: {shipment.destination_country_id.name}")
                if hasattr(shipment, 'origin_customs_id') and shipment.origin_customs_id:
                    route_lines.append(f"  - Aduana Origen: {shipment.origin_customs_id.name}")
                if hasattr(shipment, 'destination_customs_id') and shipment.destination_customs_id:
                    route_lines.append(f"  - Aduana Destino: {shipment.destination_customs_id.name}")
                if route_lines:
                    lines.append("")
                    lines.append("🗺️ RUTAS:")
                    lines.extend(route_lines)

            # Facturas
            if wizard.include_customer_invoices or wizard.include_supplier_invoices:
                if hasattr(shipment, 'external_account_ids'):
                    customer_accounts = shipment.external_account_ids.filtered(lambda a: a.type == 'customer')
                    supplier_accounts = shipment.external_account_ids.filtered(lambda a: a.type == 'supplier')

                    if wizard.include_customer_invoices and customer_accounts:
                        lines.append("")
                        lines.append(f"💰 FACTURAS CLIENTE ({len(customer_accounts)}):")
                        for acc in customer_accounts[:5]:
                            partner_name = acc.partner_id.name if acc.partner_id else 'Sin definir'
                            lines.append(f"  - {partner_name}")
                        if len(customer_accounts) > 5:
                            lines.append(f"  ... y {len(customer_accounts) - 5} más")

                    if wizard.include_supplier_invoices and supplier_accounts:
                        lines.append("")
                        lines.append(f"💳 FACTURAS PROVEEDOR ({len(supplier_accounts)}):")
                        for acc in supplier_accounts[:5]:
                            partner_name = acc.partner_id.name if acc.partner_id else 'Sin definir'
                            lines.append(f"  - {partner_name}")
                        if len(supplier_accounts) > 5:
                            lines.append(f"  ... y {len(supplier_accounts) - 5} más")

            wizard.preview_text = '\n'.join(lines) if lines else 'No hay datos para incluir en la plantilla'

    def action_create_template(self):
        """Crea la plantilla desde el embarque"""
        self.ensure_one()

        if not self.template_name:
            raise UserError(_('Debe ingresar un nombre para la plantilla'))

        # Crear valores base de la plantilla
        vals = {
            'name': self.template_name,
            'notes': self.notes,
            'company_id': self.shipment_id.company_id.id if self.shipment_id.company_id else self.env.company.id,
        }

        shipment = self.shipment_id

        # Socios
        if self.include_partners:
            if shipment.partner_id:
                vals['partner_id'] = shipment.partner_id.id
            if hasattr(shipment, 'importer_exporter_id') and shipment.importer_exporter_id:
                vals['importer_exporter_id'] = shipment.importer_exporter_id.id
            if hasattr(shipment, 'freight_agency_id') and shipment.freight_agency_id:
                vals['freight_agency_id'] = shipment.freight_agency_id.id
            if hasattr(shipment, 'carrier_id') and shipment.carrier_id:
                vals['carrier_id'] = shipment.carrier_id.id
            if hasattr(shipment, 'customs_agency_id') and shipment.customs_agency_id:
                vals['customs_agency_id'] = shipment.customs_agency_id.id
            if hasattr(shipment, 'customs_broker_person_id') and shipment.customs_broker_person_id:
                vals['customs_broker_person_id'] = shipment.customs_broker_person_id.id
            if hasattr(shipment, 'good_carrier_id') and shipment.good_carrier_id:
                vals['good_carrier_id'] = shipment.good_carrier_id.id

        # Transporte
        if self.include_transport:
            if hasattr(shipment, 'transport_type') and shipment.transport_type:
                vals['transport_type'] = shipment.transport_type
            if hasattr(shipment, 'incoterm') and shipment.incoterm:
                vals['incoterm'] = shipment.incoterm
            if hasattr(shipment, 'vessel_flight_name') and shipment.vessel_flight_name:
                vals['vessel_flight_name'] = shipment.vessel_flight_name
            if hasattr(shipment, 'voyage_number') and shipment.voyage_number:
                vals['voyage_number'] = shipment.voyage_number

        # Mercancía
        if self.include_goods:
            if hasattr(shipment, 'goods_description') and shipment.goods_description:
                vals['goods_description'] = shipment.goods_description
            if hasattr(shipment, 'commercial_value_usd') and shipment.commercial_value_usd:
                vals['commercial_value_usd'] = shipment.commercial_value_usd
            if hasattr(shipment, 'gross_weight_kg') and shipment.gross_weight_kg:
                vals['gross_weight_kg'] = shipment.gross_weight_kg
            if hasattr(shipment, 'volume_m3') and shipment.volume_m3:
                vals['volume_m3'] = shipment.volume_m3

        # Rutas
        if self.include_routes:
            if hasattr(shipment, 'origin_country_id') and shipment.origin_country_id:
                vals['origin_country_id'] = shipment.origin_country_id.id
            if hasattr(shipment, 'origin_state_id') and shipment.origin_state_id:
                vals['origin_state_id'] = shipment.origin_state_id.id
            if hasattr(shipment, 'origin_customs_id') and shipment.origin_customs_id:
                vals['origin_customs_id'] = shipment.origin_customs_id.id
            if hasattr(shipment, 'loading_port_airport_id') and shipment.loading_port_airport_id:
                vals['loading_port_airport_id'] = shipment.loading_port_airport_id.id
            if hasattr(shipment, 'transshipment_port_airport_ids') and shipment.transshipment_port_airport_ids:
                vals['transshipment_port_airport_ids'] = [(6, 0, shipment.transshipment_port_airport_ids.ids)]
            if hasattr(shipment, 'destination_country_id') and shipment.destination_country_id:
                vals['destination_country_id'] = shipment.destination_country_id.id
            if hasattr(shipment, 'destination_state_id') and shipment.destination_state_id:
                vals['destination_state_id'] = shipment.destination_state_id.id
            if hasattr(shipment, 'destination_customs_id') and shipment.destination_customs_id:
                vals['destination_customs_id'] = shipment.destination_customs_id.id
            if hasattr(shipment, 'unloading_port_airport_id') and shipment.unloading_port_airport_id:
                vals['unloading_port_airport_id'] = shipment.unloading_port_airport_id.id

        # Contactos
        if self.include_contacts:
            if hasattr(shipment, 'freight_agency_contact_name') and shipment.freight_agency_contact_name:
                vals['freight_agency_contact_name'] = shipment.freight_agency_contact_name
            if hasattr(shipment, 'customs_agency_contact') and shipment.customs_agency_contact:
                vals['customs_agency_contact'] = shipment.customs_agency_contact
            if hasattr(shipment, 'ground_carrier_contact') and shipment.ground_carrier_contact:
                vals['ground_carrier_contact'] = shipment.ground_carrier_contact
            if hasattr(shipment, 'vehicle_plate') and shipment.vehicle_plate:
                vals['vehicle_plate'] = shipment.vehicle_plate
            if hasattr(shipment, 'driver_name') and shipment.driver_name:
                vals['driver_name'] = shipment.driver_name

        # Estados
        if self.include_states:
            if hasattr(shipment, 'state') and shipment.state:
                vals['state'] = shipment.state
            if hasattr(shipment, 'importer_exporter_state') and shipment.importer_exporter_state:
                vals['importer_exporter_state'] = shipment.importer_exporter_state
            if hasattr(shipment, 'freight_agency_state') and shipment.freight_agency_state:
                vals['freight_agency_state'] = shipment.freight_agency_state
            if hasattr(shipment, 'carrier_state') and shipment.carrier_state:
                vals['carrier_state'] = shipment.carrier_state
            if hasattr(shipment, 'customs_agency_state') and shipment.customs_agency_state:
                vals['customs_agency_state'] = shipment.customs_agency_state
            if hasattr(shipment, 'customs_broker_person_state') and shipment.customs_broker_person_state:
                vals['customs_broker_person_state'] = shipment.customs_broker_person_state
            if hasattr(shipment, 'good_carrier_state') and shipment.good_carrier_state:
                vals['good_carrier_state'] = shipment.good_carrier_state

        # Configuración
        if self.include_config:
            if hasattr(shipment, 'property_payment_term_id') and shipment.property_payment_term_id:
                vals['property_payment_term_id'] = shipment.property_payment_term_id.id
            if hasattr(shipment, 'currency_id') and shipment.currency_id:
                vals['currency_id'] = shipment.currency_id.id
            if hasattr(shipment, 'tag_ids') and shipment.tag_ids:
                vals['tag_ids'] = [(6, 0, shipment.tag_ids.ids)]

        # Crear la plantilla
        template = self.env['adroc.shipment.template'].create(vals)

        # Crear plantillas de factura desde cuentas ajenas
        if hasattr(shipment, 'external_account_ids'):
            if self.include_customer_invoices:
                customer_accounts = shipment.external_account_ids.filtered(lambda a: a.type == 'customer')
                for account in customer_accounts:
                    self._create_invoice_template_from_account(template, account, 'customer')

            if self.include_supplier_invoices:
                supplier_accounts = shipment.external_account_ids.filtered(lambda a: a.type == 'supplier')
                for account in supplier_accounts:
                    self._create_invoice_template_from_account(template, account, 'supplier')

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Plantilla Creada'),
                'message': _('La plantilla "%s" se ha creado exitosamente.') % template.name,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'adroc.shipment.template',
                    'res_id': template.id,
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                },
            }
        }

    def _create_invoice_template_from_account(self, template, account, invoice_type):
        """Crea una plantilla de factura desde una cuenta ajena"""
        invoice_vals = {
            'template_id': template.id,
            'invoice_type': invoice_type,
            'name': account.name or f"Factura {invoice_type}",
            'partner_id': account.partner_id.id if account.partner_id else False,
            'document_type': account.document_type if hasattr(account, 'document_type') else False,
        }

        invoice_template = self.env['adroc.shipment.template.invoice'].create(invoice_vals)

        # Crear líneas si existen
        if hasattr(account, 'line_ids'):
            for line in account.line_ids:
                line_vals = {
                    'invoice_template_id': invoice_template.id,
                    'name': line.name if hasattr(line, 'name') else False,
                    'product_id': line.product_id.id if hasattr(line, 'product_id') and line.product_id else False,
                    'quantity': line.quantity if hasattr(line, 'quantity') else 1.0,
                    'price_unit': line.price_unit if hasattr(line, 'price_unit') else 0.0,
                    'tag_ids': [(6, 0, line.tag_ids.ids)] if hasattr(line, 'tag_ids') and line.tag_ids else False,
                }
                self.env['adroc.shipment.template.invoice.line'].create(line_vals)
