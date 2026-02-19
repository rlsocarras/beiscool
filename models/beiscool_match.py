# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class BeiscoolMatch(models.Model):
    _name = 'beiscool.match'
    _description = 'Partido de Béisbol'
    _order = 'match_date, sequence'

    name = fields.Char(
        string='Nombre',
        required=True,
        size=200,
    )

    copa_id = fields.Many2one(
        'beiscool.copa',
        string='Copa',
        ondelete='cascade',
        required=True,
    )

    home_team_id = fields.Many2one(
        'beiscool.team',
        string='Equipo Local',
        required=True,
    )

    away_team_id = fields.Many2one(
        'beiscool.team',
        string='Equipo Visitante',
        required=True,
    )

    home_runs = fields.Integer(
        string='Carreras Local',
        default=0,
    )

    away_runs = fields.Integer(
        string='Carreras Visitante',
        default=0,
    )

    winner_id = fields.Many2one(
        'beiscool.team',
        string='Ganador',
        compute='_compute_winner',
        store=True,
    )

    match_date = fields.Datetime(
        string='Fecha y Hora',
        required=False,
    )
    
    match_date_formatted = fields.Char(
        string='Fecha Formateada',
        compute='_compute_match_date_formatted',
        store=False,
    )
    
    @api.depends('match_date')
    def _compute_match_date_formatted(self):
        for record in self:
            if record.match_date:
                # Usar la fecha directamente sin conversión de timezone
                # Parsear el datetime almacenado
                dt = fields.Datetime.from_string(record.match_date)
                day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                day_name = day_names[dt.weekday()]
                record.match_date_formatted = f"{day_name}, {dt.strftime('%d/%m/%Y %H:%M')}"
            else:
                record.match_date_formatted = False

    state = fields.Selection(
        [
            ('scheduled', 'Programado'),
            ('played', 'Jugado'),
            ('cancelled', 'Cancelado'),
        ],
        string='Estado',
        default='scheduled',
    )

    stage = fields.Selection(
        [
            ('round_robin', 'Round Robin'),
            ('semifinal', 'Semifinal'),
            ('final', 'Final'),
        ],
        string='Etapa',
        default='round_robin',
    )

    sequence = fields.Integer(
        string='Secuencia',
        default=0,
    )

    # Integración con calendario de Odoo
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Evento de Calendario',
        copy=False,
    )

    # Campos calculados
    is_tied = fields.Boolean(
        string='Empate',
        compute='_compute_is_tied',
        store=True,
    )

    display_score = fields.Char(
        string='Marcador',
        compute='_compute_display_score',
        store=True,
    )

    @api.depends('home_runs', 'away_runs', 'state')
    def _compute_winner(self):
        for record in self:
            if record.state != 'played':
                record.winner_id = False
            elif record.home_runs > record.away_runs:
                record.winner_id = record.home_team_id.id
            elif record.away_runs > record.home_runs:
                record.winner_id = record.away_team_id.id
            else:
                record.winner_id = False

    @api.depends('home_runs', 'away_runs')
    def _compute_is_tied(self):
        for record in self:
            record.is_tied = record.home_runs == record.away_runs

    @api.depends('home_runs', 'away_runs', 'state')
    def _compute_display_score(self):
        for record in self:
            if record.state == 'scheduled':
                record.display_score = 'vs'
            else:
                record.display_score = f'{record.home_runs} - {record.away_runs}'

    @api.onchange('home_team_id', 'away_team_id')
    def _onchange_teams(self):
        if self.home_team_id and self.away_team_id:
            if self.home_team_id == self.away_team_id:
                raise UserError('El equipo local y el visitante no pueden ser el mismo.')

    @api.onchange('home_runs', 'away_runs')
    def _onchange_score(self):
        if self.home_runs is not None and self.away_runs is not None:
            if self.state == 'scheduled':
                self.state = 'played'

    def action_play(self):
        """Marcar partido como jugado"""
        if not self.home_runs and not self.away_runs:
            raise UserError('Debe ingresar el marcador antes de marcar el partido como jugado.')
        
        self.write({'state': 'played'})
        
        # Recalcular tabla de posiciones
        if self.copa_id:
            self.copa_id._compute_standings()
            
            # Si es semifinal o final, generar siguiente partido
            if self.stage == 'semifinal':
                self.copa_id._generate_final()
            # Si es final, actualizar estado de la copa
            elif self.stage == 'final' and self.winner_id:
                self.copa_id.write({'state': 'finished', 'champion_id': self.winner_id.id})

    def action_cancel(self):
        """Cancelar partido"""
        self.write({'state': 'cancelled'})
        
        # Recalcular tabla de posiciones
        if self.copa_id:
            self.copa_id._compute_standings()

    def action_reset(self):
        """Restablecer partido a programado"""
        self.write({'state': 'scheduled'})
        
        # Recalcular tabla de posiciones
        if self.copa_id:
            self.copa_id._compute_standings()

    def write(self, vals):
        """Override write to update standings when match changes"""
        result = super(BeiscoolMatch, self).write(vals)
        
        # Si se actualizó el marcador o el estado, recalcular standings
        if 'home_runs' in vals or 'away_runs' in vals or 'state' in vals:
            for record in self:
                if record.copa_id and record.state == 'played':
                    record.copa_id._compute_standings()
        
        return result
