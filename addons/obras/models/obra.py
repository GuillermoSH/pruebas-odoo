from odoo import models, fields, api

class Obra(models.Model):
    _name = 'obras.obra'
    _description = 'Registro de Obras'

    name = fields.Char(string='Obra', required=True)

    stage_id = fields.Many2one(
        'crm.stage', 
        string='Etapa', 
        group_expand='_read_group_stage_ids', # Para que aparezcan las columnas vacías
        default=lambda self: self.env['crm.stage'].search([], limit=1),
    )

    coste = fields.Float(string='Coste de Obra')
    aceptada = fields.Boolean(string='Aceptada', default=False)

    iva = fields.Float(string='IVA (21%)', compute='_compute_iva')

    total = fields.Float(string='Total con IVA', compute='_compute_total', store=True) # Para almacenar el valor calculado en la base de datos

    @api.depends('coste')
    def _compute_iva(self):
        for record in self:
            record.iva = record.coste * 0.21

    @api.depends('coste', 'iva')
    def _compute_total(self):
        for record in self:
            record.total = record.coste + record.iva

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        return stages.search([])