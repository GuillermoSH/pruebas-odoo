from odoo import models, fields

class Obra(models.Model):
    _name = 'obras.obra'
    _description = 'Registro de Obras'

    # Campo string (texto corto)
    name = fields.Char(string='Obra', required=True)
    
    # Campo float (número con decimales)
    coste = fields.Float(string='Coste de Obra')
    
    # Campo booleano (check de sí/no)
    aceptada = fields.Boolean(string='Aceptada', default=False)