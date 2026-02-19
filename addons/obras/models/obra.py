from odoo import models, fields, api

class Obra(models.Model):
    _name = 'obras.obra'
    _description = 'Registro de Obras'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Obra', required=True, tracking=True)

    partner_id = fields.Many2one(
        'res.partner', 
        string='Cliente', 
        required=False,
        tracking=False
    )
    
    company_id = fields.Many2one(
        'res.company', 
        string='Compañía', 
        required=False,
        default=lambda self: self.env.company,
    )

    stage_id = fields.Many2one(
        'crm.stage', 
        string='Etapa', 
        group_expand='_read_group_stage_ids', # Para que aparezcan las columnas vacías
        default=lambda self: self.env['crm.stage'].search([], limit=1),
    )

    kanban_state = fields.Selection([
        ('done', 'En curso'),
        ('blocked', 'Urgencia'),
        ('normal', 'Atención'),
        ('warning', 'Llamar'),
    ], string='Estado', default='done', required=True)

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

    def write(self, vals):
        res = super(Obra, self).write(vals)
        
        if 'kanban_state' in vals and vals.get('kanban_state') == 'blocked':
            for record in self:
                # Creamos la actividad vinculada al registro
                record.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=self.env.user.id,
                    summary='¡URGENCIA DETECTADA!',
                    note=f'Se ha marcado la obra "{record.name}" como Urgente... Se debe revisar de inmediato.'
                )
        return res