# -*- coding: utf-8 -*-
{
    'name': 'Adroc - Shipment Templates',
    'version': '19.0.1.1.0',
    'category': 'Logistics',
    'summary': 'Sistema de plantillas para embarques y cuentas ajenas',
    'description': """
        Modulo para gestionar plantillas de autocompletado:
        - Plantillas de embarques (mrdc.shipment)
        - Plantillas de facturas proveedor
        - Plantillas de facturas cliente
        - Crear plantillas desde embarques existentes
        - Usar embarques como plantillas directamente

        Permite cargar plantillas mediante un wizard con vista previa
        de los datos que se cargarán.

        Características:
        - Cargar Plantilla: Carga datos desde plantillas guardadas
        - Crear Plantilla: Crea una plantilla desde el embarque actual
        - Cargar desde Embarque: Carga datos desde otro embarque marcado como plantilla
        - Marcar embarque como plantilla directamente

        Permisos:
        - Usuarios normales pueden usar y crear plantillas
        - Solo administradores pueden eliminar plantillas
    """,
    'author': 'Adroc',
    'website': 'https://portfolio.adrocgt.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'mrdc_shipment_base',
        'mrdc_shipment_importer_exporter',
        'mrdc_shipment_carrier',
        'mrdc_shipment_freight_agency',
        'mrdc_shipment_customs_agency',
        'mrdc_shipment_customs_broker_person',
        'mrdc_shipment_good_carrier',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/adroc_shipment_template_views.xml',
        'views/load_template_wizard_views.xml',
        'views/create_template_wizard_views.xml',
        'views/mrdc_shipment_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
