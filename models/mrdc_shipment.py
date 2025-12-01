# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrdcShipment(models.Model):
    _inherit = 'mrdc.shipment'

    def action_open_load_template_wizard(self):
        """Abre el wizard para cargar una plantilla"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cargar Plantilla',
            'res_model': 'adroc.load.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_shipment_id': self.id,
            }
        }

    def action_open_create_template_wizard(self):
        """Abre el wizard para crear una plantilla desde este embarque"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Crear Plantilla',
            'res_model': 'adroc.create.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_shipment_id': self.id,
                'default_template_name': f"Plantilla - {self.name}" if self.name else "Nueva Plantilla",
            }
        }

