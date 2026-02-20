from odoo import models, fields, api

class Obra(models.Model):
    _name = 'obras.obra'
    _description = 'Registro de Obras'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Obra', required=True, tracking=True)

    priority = fields.Selection([
        ('0', 'Baja'),
        ('1', 'Media'),
        ('2', 'Alta'),
        ('3', 'Muy Alta'),
    ], string='Prioridad', default='0', tracking=True)

    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True, tracking=True, default=fields.Date.context_today)
    fecha_fin = fields.Date(string='Fecha de Fin', required=True, tracking=True)

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

    @api.constrains('fecha_inicio', 'fecha_fin')
    # Validacion para que la fecha de fin no sea anterior a la fecha de inicio
    def _check_dates(self):
        for record in self:
            if record.fecha_inicio and record.fecha_fin and record.fecha_inicio > record.fecha_fin:
                raise ValidationError(_('La fecha de fin no puede ser anterior a la fecha de inicio.'))

    @api.onchange('fecha_fin')
    def _onchange_fecha_fin(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin < self.fecha_inicio:
                # Al resetear el valor, el usuario entiende visualmente que no es válido
                self.fecha_fin = self.fecha_inicio 
                return {
                    'warning': {
                        'title': "Aviso de Planificación",
                        'message': "La fecha de fin se ha ajustado para que coincida con el inicio, ya que no puede ser anterior.",
                        'type': 'notification', # Aparece como una burbuja/sticker arriba a la derecha
                    }
                }

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