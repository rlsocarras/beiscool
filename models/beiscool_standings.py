# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BeiscoolStandings(models.Model):
    _name = 'beiscool.standings'
    _description = 'Tabla de Posiciones'
    _order = 'matches_won desc, run_differential desc, runs_scored desc'

    copa_id = fields.Many2one(
        'beiscool.copa',
        string='Copa',
        ondelete='cascade',
        required=True,
    )

    team_id = fields.Many2one(
        'beiscool.team',
        string='Equipo',
        required=True,
    )

    matches_played = fields.Integer(
        string='Partidos Jugados',
        default=0,
    )

    matches_won = fields.Integer(
        string='Partidos Ganados',
        default=0,
    )

    matches_lost = fields.Integer(
        string='Partidos Perdidos',
        default=0,
    )

    runs_scored = fields.Integer(
        string='Carreras Anotadas',
        default=0,
    )

    runs_allowed = fields.Integer(
        string='Carreras Permitidas',
        default=0,
    )

    run_differential = fields.Integer(
        string='Diferencia de Carreras',
        default=0,
    )

    points = fields.Integer(
        string='Puntos',
        default=0,
    )

    # Campos calculados para ordenamiento
    position = fields.Integer(
        string='Posición',
        compute='_compute_position',
        store=True,
    )

    @api.depends('copa_id.standings_ids', 'matches_won', 'run_differential', 'runs_scored')
    def _compute_position(self):
        """Calcula la posición del equipo en la tabla"""
        for record in self:
            if not record.copa_id:
                record.position = 0
                continue
            
            # Obtener todos los standings de la copa ordenados
            all_standings = record.copa_id.standings_ids.sorted(
                key=lambda x: (x.matches_won, x.run_differential, x.runs_scored),
                reverse=True
            )
            
            # Encontrar la posición de este equipo
            position = 1
            for standing in all_standings:
                if standing == record:
                    record.position = position
                    break
                position += 1

    # ============================================
    # MÉTODOS DE DESEMPATE
    # ============================================

    def get_head_to_head_result(self, other_team):
        """
        Obtiene el resultado del encuentro directo entre dos equipos.
        Retorna: 1 si self gana, -1 si other_team gana, 0 si empate
        """
        self.ensure_one()
        
        if not self.copa_id or not other_team:
            return 0
        
        # Obtener partidos jugados entre estos dos equipos
        matches = self.copa_id.match_ids.filtered(
            lambda m: m.state == 'played' and
            ((m.home_team_id == self.team_id and m.away_team_id == other_team) or
             (m.home_team_id == other_team and m.away_team_id == self.team_id))
        )
        
        if not matches:
            return 0
        
        # Contar victorias
        wins_self = 0
        wins_other = 0
        
        for match in matches:
            if match.winner_id == self.team_id:
                wins_self += 1
            elif match.winner_id == other_team:
                wins_other += 1
        
        if wins_self > wins_other:
            return 1
        elif wins_other > wins_self:
            return -1
        else:
            return 0

    def get_tiebreaker_rank(self, other_standings_list):
        """
        Calcula el ranking de desempate para múltiples equipos empatados.
        Retorna una tupla con los criterios de desempate.
        """
        self.ensure_one()
        
        return (
            -self.matches_won,  # Más partidos ganados
            -self.run_differential,  # Mayor diferencia de carreras
            -self.runs_scored,  # Más carreras anotadas
        )
