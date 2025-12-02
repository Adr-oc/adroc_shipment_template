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

    # Líneas de campos seleccionables
    field_line_ids = fields.One2many(
        'adroc.create.template.wizard.line',
        'wizard_id',
        string='Campos a Incluir'
    )

    # Opciones de facturas
    include_customer_invoices = fields.Boolean(
        string='Incluir Facturas Cliente',
        default=True
    )
    include_supplier_invoices = fields.Boolean(
        string='Incluir Facturas Proveedor',
        default=True
    )

    customer_invoice_count = fields.Integer(
        string='Facturas Cliente',
        compute='_compute_invoice_counts'
    )
    supplier_invoice_count = fields.Integer(
        string='Facturas Proveedor',
        compute='_compute_invoice_counts'
    )

    @api.depends('shipment_id')
    def _compute_invoice_counts(self):
        for wizard in self:
            if wizard.shipment_id and hasattr(wizard.shipment_id, 'external_account_ids'):
                wizard.customer_invoice_count = len(wizard.shipment_id.external_account_ids.filtered(
                    lambda a: a.move_type == 'out_invoice'
                ))
                wizard.supplier_invoice_count = len(wizard.shipment_id.external_account_ids.filtered(
                    lambda a: a.move_type == 'in_invoice'
                ))
            else:
                wizard.customer_invoice_count = 0
                wizard.supplier_invoice_count = 0

    def _get_excluded_fields(self):
        """Campos que NO deben ser incluidos en la plantilla"""
        return {
            # Campos del sistema
            'id', 'create_date', 'create_uid', 'write_date', 'write_uid',
            '__last_update', 'display_name',
            # Campos de identificación única
            'name', 'external_id', 'instance',
            # Campos computados/relacionados que no se deben copiar
            'company_id',  # Se asigna de la compañía actual
            'message_ids', 'message_follower_ids', 'message_partner_ids',
            'message_channel_ids', 'message_main_attachment_id',
            'message_has_error', 'message_has_error_counter',
            'message_needaction', 'message_needaction_counter',
            'message_attachment_count', 'message_is_follower',
            'activity_ids', 'activity_state', 'activity_user_id',
            'activity_type_id', 'activity_type_icon', 'activity_date_deadline',
            'activity_summary', 'activity_exception_decoration', 'activity_exception_icon',
            'my_activity_date_deadline', 'has_message',
            # Campos de conteo
            'purchase_count', 'sale_count', 'account_move_partner_count',
            'account_move_supplier_count', 'external_account_count',
            # One2many (relaciones inversas)
            'external_account_ids', 'summary_ids', 'event_ids', 'detail_ids',
            # Campos de estado que son computados
            'state',  # El estado general
            # Campos de sincronización
            'mrdc_shipment_sync_id', 'mrdc_shipment_properties',
        }

    def _get_field_category(self, field_name, field_obj):
        """Determina la categoría de un campo basándose en su nombre y tipo"""
        name_lower = field_name.lower()

        # Categorías por nombre de campo
        if any(x in name_lower for x in ['partner', 'importer', 'exporter', 'freight', 'carrier', 'customs', 'agency', 'broker']):
            if 'contact' in name_lower or 'phone' in name_lower or 'email' in name_lower:
                return 'Contactos'
            if 'state' in name_lower:
                return 'Estados'
            return 'Socios'

        if any(x in name_lower for x in ['transport', 'vessel', 'flight', 'voyage', 'incoterm', 'vehicle', 'driver', 'plate']):
            return 'Transporte'

        if any(x in name_lower for x in ['goods', 'weight', 'volume', 'value', 'commercial', 'description', 'quantity', 'package']):
            return 'Mercancía'

        if any(x in name_lower for x in ['origin', 'destination', 'country', 'port', 'airport', 'customs', 'loading', 'unloading', 'transshipment', 'route']):
            return 'Rutas'

        if any(x in name_lower for x in ['contact', 'phone', 'email', 'mobile']):
            return 'Contactos'

        if any(x in name_lower for x in ['state', 'status']):
            return 'Estados'

        if any(x in name_lower for x in ['date', 'eta', 'etd', 'ata', 'atd']):
            return 'Fechas'

        if any(x in name_lower for x in ['ref', 'reference', 'number', 'no', 'bl', 'awb', 'booking']):
            return 'Referencias'

        if any(x in name_lower for x in ['currency', 'payment', 'term', 'tag', 'note']):
            return 'Configuración'

        return 'Otros'

    def _get_field_display_value(self, shipment, field_name):
        """Obtiene el valor de visualización de un campo"""
        try:
            value = getattr(shipment, field_name, None)
            if value is None:
                return ''

            # Manejar campos vacíos
            if isinstance(value, bool) and not value:
                return ''
            if isinstance(value, (list, tuple)) and not value:
                return ''

            field = shipment._fields.get(field_name)
            if not field:
                return str(value) if value else ''

            if field.type == 'many2one':
                if value:
                    return value.display_name or getattr(value, 'name', str(value.id))
                return ''
            elif field.type == 'many2many':
                if value:
                    names = value.mapped(lambda r: r.display_name or getattr(r, 'name', ''))
                    return ', '.join(filter(None, names))
                return ''
            elif field.type == 'one2many':
                return f"({len(value)} registros)" if value else ''
            elif field.type == 'selection':
                if value and hasattr(field, 'selection'):
                    selection = field.selection
                    if callable(selection):
                        selection = selection(shipment)
                    selection_dict = dict(selection)
                    return selection_dict.get(value, value)
                return str(value) if value else ''
            elif field.type == 'boolean':
                return 'Sí' if value else ''
            elif field.type in ('float', 'monetary'):
                return f"{value:,.2f}" if value else ''
            elif field.type == 'integer':
                return str(value) if value else ''
            elif field.type == 'date':
                return str(value) if value else ''
            elif field.type == 'datetime':
                return str(value) if value else ''
            elif field.type in ('text', 'html'):
                if value:
                    text = str(value)
                    return text[:100] + '...' if len(text) > 100 else text
                return ''
            else:
                return str(value) if value else ''
        except Exception:
            return ''

    def _has_value(self, value, field_type):
        """Verifica si un valor no está vacío según su tipo"""
        if value is None:
            return False
        if field_type == 'boolean':
            return value is True
        if field_type in ('many2one',):
            return bool(value)
        if field_type in ('many2many', 'one2many'):
            return len(value) > 0
        if field_type in ('integer', 'float', 'monetary'):
            return value != 0
        if field_type in ('char', 'text', 'html', 'selection'):
            return bool(value)
        if field_type in ('date', 'datetime'):
            return bool(value)
        return bool(value)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        shipment_id = self._context.get('default_shipment_id')
        if not shipment_id and self._context.get('active_model') == 'mrdc.shipment':
            shipment_id = self._context.get('active_id')

        if shipment_id:
            shipment = self.env['mrdc.shipment'].browse(shipment_id)
            res['shipment_id'] = shipment.id
            res['template_name'] = f"Plantilla - {shipment.name}" if shipment.name else "Nueva Plantilla"

            # Obtener campos excluidos
            excluded = self._get_excluded_fields()

            # Generar líneas de campos dinámicamente
            field_lines = []

            # Obtener TODOS los campos del modelo mrdc.shipment
            for field_name, field_obj in shipment._fields.items():
                # Excluir campos del sistema y no deseados
                if field_name in excluded:
                    continue

                # Excluir campos computados sin store (no se pueden copiar)
                if field_obj.compute and not field_obj.store:
                    continue

                # Excluir campos relacionados
                if field_obj.related:
                    continue

                # Excluir One2many (son relaciones inversas)
                if field_obj.type == 'one2many':
                    continue

                # Verificar si el campo tiene valor
                try:
                    value = getattr(shipment, field_name)
                    if not self._has_value(value, field_obj.type):
                        continue
                except Exception:
                    continue

                # Obtener valor de visualización
                display_value = self._get_field_display_value(shipment, field_name)
                if not display_value:
                    continue

                # Obtener etiqueta del campo (requerido - validación estricta)
                field_label = ''
                if field_obj.string and str(field_obj.string).strip():
                    field_label = str(field_obj.string).strip()
                if not field_label:
                    field_label = field_name.replace('_', ' ').title()
                if not field_label:
                    field_label = field_name
                if not field_label:
                    continue  # Saltar si no hay etiqueta válida

                # Obtener categoría
                category = self._get_field_category(field_name, field_obj) or 'Otros'

                # Validar que todos los campos requeridos tengan valor
                if not field_name or not field_label:
                    continue

                field_lines.append((0, 0, {
                    'field_name': str(field_name),
                    'field_label': str(field_label),
                    'category': str(category),
                    'current_value': str(display_value) if display_value else '-',
                    'include': True,
                }))

            # Ordenar por categoría y luego por etiqueta
            field_lines.sort(key=lambda x: (x[2].get('category', ''), x[2].get('field_label', '')))
            res['field_line_ids'] = field_lines

        return res

    def action_select_all(self):
        """Selecciona todos los campos"""
        self.field_line_ids.write({'include': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_deselect_all(self):
        """Deselecciona todos los campos"""
        self.field_line_ids.write({'include': False})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_template(self):
        """Crea la plantilla desde el embarque con los campos seleccionados"""
        self.ensure_one()

        if not self.template_name:
            raise UserError(_('Debe ingresar un nombre para la plantilla'))

        selected_lines = self.field_line_ids.filtered(lambda l: l.include)
        if not selected_lines and not self.include_customer_invoices and not self.include_supplier_invoices:
            raise UserError(_('Debe seleccionar al menos un campo o incluir facturas'))

        shipment = self.shipment_id

        # Construir datos JSON con los campos seleccionados
        import json
        template_data = []

        for line in selected_lines:
            field_name = line.field_name
            if not field_name or not hasattr(shipment, field_name):
                continue

            field = shipment._fields.get(field_name)
            if not field:
                continue

            try:
                value = getattr(shipment, field_name)
                if not self._has_value(value, field.type):
                    continue

                # Preparar el valor según el tipo
                if field.type == 'many2one':
                    stored_value = value.id if value else False
                elif field.type == 'many2many':
                    stored_value = value.ids if value else []
                elif field.type in ('date', 'datetime'):
                    stored_value = str(value) if value else False
                else:
                    stored_value = value

                template_data.append({
                    'field': field_name,
                    'label': line.field_label or field_name,
                    'category': line.category or 'Otros',
                    'type': field.type,
                    'value': stored_value,
                    'display_value': line.current_value or str(stored_value),
                })
            except Exception:
                continue

        # Crear valores base de la plantilla
        vals = {
            'name': self.template_name,
            'notes': self.notes,
            'company_id': shipment.company_id.id if shipment.company_id else self.env.company.id,
            'template_data': json.dumps(template_data, ensure_ascii=False, default=str),
        }

        # Crear la plantilla
        template = self.env['adroc.shipment.template'].create(vals)

        # Crear plantillas de factura desde cuentas ajenas
        if hasattr(shipment, 'external_account_ids'):
            if self.include_customer_invoices:
                customer_accounts = shipment.external_account_ids.filtered(
                    lambda a: a.move_type == 'out_invoice'
                )
                for account in customer_accounts:
                    self._create_invoice_template_from_account(template, account, 'customer')

            if self.include_supplier_invoices:
                supplier_accounts = shipment.external_account_ids.filtered(
                    lambda a: a.move_type == 'in_invoice'
                )
                for account in supplier_accounts:
                    self._create_invoice_template_from_account(template, account, 'supplier')

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Plantilla Creada'),
                'message': _('La plantilla "%s" se ha creado con %d campos.') % (
                    template.name, len(selected_lines)
                ),
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
                    'description': line.ref if hasattr(line, 'ref') else False,
                    'product_id': line.product_id.id if hasattr(line, 'product_id') and line.product_id else False,
                    'amount': line.amount if hasattr(line, 'amount') else 0.0,
                    'currency_id': line.currency_id.id if hasattr(line, 'currency_id') and line.currency_id else False,
                }
                self.env['adroc.shipment.template.invoice.line'].create(line_vals)


class AdrocCreateTemplateWizardLine(models.TransientModel):
    _name = 'adroc.create.template.wizard.line'
    _description = 'Línea de Campo para Plantilla'
    _order = 'category, field_label'

    wizard_id = fields.Many2one(
        'adroc.create.template.wizard',
        string='Wizard',
        ondelete='cascade'
    )
    field_name = fields.Char(
        string='Nombre Técnico'
    )
    field_label = fields.Char(
        string='Campo'
    )
    category = fields.Char(
        string='Categoría'
    )
    current_value = fields.Char(
        string='Valor Actual'
    )
    include = fields.Boolean(
        string='Incluir',
        default=True
    )
