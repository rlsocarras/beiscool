# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import math


class BeiscoolCopa(models.Model):
    _name = 'beiscool.copa'
    _description = 'Copa de Béisbol'
    _order = 'date_start desc, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        size=200,
    )

    date_start = fields.Date(
        string='Fecha de Inicio',
        required=False,
    )

    date_end = fields.Date(
        string='Fecha de Fin',
        required=False,
    )

    location = fields.Char(
        string='Lugar',
        size=300,
    )

    organizer = fields.Char(
        string='Organizador',
        size=200,
    )

    description = fields.Text(
        string='Descripción',
    )

    captain_ids = fields.Many2many(
        'beiscool.player',
        'beiscool_copa_captain_rel',
        'copa_id',
        'player_id',
        string='Capitanes',
    )

    team_quantity = fields.Integer(
        string='Cantidad de Equipos',
        compute='_compute_team_quantity',
        store=False,
    )

    player_quantity = fields.Integer(
        string='Cantidad de Jugadores',
        default=0,
        compute='_compute_player_quantity',
        store=True,
    )

    captain_count = fields.Integer(
        string='Cantidad de Capitanes',
        default=0,
        compute='_compute_captain_count',
        store=True,
    )

    match_count = fields.Integer(
        string='Cantidad de Partidos',
        default=0,
        compute='_compute_match_count',
        store=True,
    )

    referee_count = fields.Integer(
        string='Cantidad de Árbitros',
        default=0,
        compute='_compute_referee_count',
        store=True,
    )

    referee_ids = fields.Many2many(
        'beiscool.referee',
        'beiscool_copa_referee_rel',
        'copa_id',
        'referee_id',
        string='Árbitros',
    )

    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('in_progress', 'En Progreso'),
            ('finished', 'Finalizado'),
        ],
        string='Estado',
        default='draft',
        readonly=True,
    )

    rounds = fields.Integer(
        string='Número de Vueltas',
        default=1,
        help='Cantidad de veces que cada equipo enfrenta a otro',
    )

    has_semifinal = fields.Boolean(
        string='Tiene Semifinal',
        default=True,
    )

    has_final = fields.Boolean(
        string='Tiene Final',
        default=True,
    )

    team_ids = fields.One2many(
        'beiscool.team',
        'copa_id',
        string='Equipos',
    )

    match_ids = fields.One2many(
        'beiscool.match',
        'copa_id',
        string='Partidos',
    )

    standings_ids = fields.One2many(
        'beiscool.standings',
        'copa_id',
        string='Tabla de Posiciones',
    )

    # Campos calculados
    matches_played = fields.Integer(
        string='Partidos Jugados',
        compute='_compute_matches_stats',
        store=True,
    )

    matches_total = fields.Integer(
        string='Total Partidos',
        compute='_compute_matches_stats',
        store=True,
    )

    champion_id = fields.Many2one(
        'beiscool.team',
        string='Campeón',
        readonly=True,
    )

    # ============================================
    # METODOS COMPUTADOS
    # ============================================

    @api.depends('team_ids')
    def _compute_team_quantity(self):
        for record in self:
            record.team_quantity = len(record.team_ids)

    @api.depends('team_ids.player_ids')
    def _compute_player_quantity(self):
        for record in self:
            total_players = 0
            for team in record.team_ids:
                total_players += len(team.player_ids)
            record.player_quantity = total_players

    @api.depends('team_ids.player_ids.is_captain')
    def _compute_captain_count(self):
        for record in self:
            total_captains = 0
            for team in record.team_ids:
                total_captains += len(team.player_ids.filtered(lambda p: p.is_captain))
            record.captain_count = total_captains

    @api.depends('match_ids')
    def _compute_match_count(self):
        for record in self:
            record.match_count = len(record.match_ids)

    @api.depends('referee_ids')
    def _compute_referee_count(self):
        for record in self:
            record.referee_count = len(record.referee_ids)

    @api.depends('match_ids', 'match_ids.state')
    def _compute_matches_stats(self):
        for record in self:
            matches = record.match_ids.filtered(lambda m: m.state == 'played')
            record.matches_played = len(matches)
            record.matches_total = len(record.match_ids)

    # ============================================
    # ACCIONES DEL MENÚ
    # ============================================

    def action_draft(self):
        """Cambiar estado a borrador"""
        self.write({'state': 'draft'})

    def action_in_progress(self):
        """Cambiar estado a en progreso"""
        if not self.team_ids:
            raise UserError('Debe agregar al menos un equipo antes de iniciar la copa.')
        if len(self.team_ids) < 2:
            raise UserError('Debe agregar al menos 2 equipos para iniciar la copa.')
        self.write({'state': 'in_progress'})

    def action_finished(self):
        """Cambiar estado a finalizado"""
        # Determinar campeón
        if self.standings_ids:
            champion = self.standings_ids[0].team_id
            self.write({
                'state': 'finished',
                'champion_id': champion.id,
            })
        else:
            self.write({'state': 'finished'})

    # ============================================
    # GENERACIÓN DE CALENDARIO
    # ============================================

    def action_generate_calendar(self):
        """Genera el calendario completo de la copa"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError('Solo puede generar el calendario en estado Borrador.')
        
        if len(self.team_ids) < 2:
            raise UserError('Debe agregar al menos 2 equipos.')
        
        # Eliminar partidos existentes
        self.match_ids.unlink()
        
        teams = self.team_ids.sorted('name')
        
        # Generar round-robin
        round_robin_matches = self._generate_round_robin(teams)
        
        # Balancear calendario
        balanced_matches = self._balance_schedule(round_robin_matches)
        
        # Crear partidos
        self._create_matches(balanced_matches, 'round_robin')
        
        # Generar semifinal si aplica
        if self.has_semifinal:
            self._generate_semifinals()
        
        # Generar final si aplica
        if self.has_final:
            self._generate_final()
        
        # Actualizar tabla de posiciones
        self._compute_standings()
        
        return True

    def _generate_round_robin(self, teams):
        """
        Algoritmo round-robin cíclico (todos contra todos)
        """
        matches = []
        n = len(teams)
        
        # Si el número de equipos es impar, añadir "bye"
        if n % 2 == 1:
            teams = teams + [False]  # False representa "bye"
            n += 1
        
        # Número de rondas
        num_rounds = n - 1
        
        # Crear lista de equipos para rotar
        team_list = list(teams)
        
        for r in range(num_rounds):
            # Rotar equipos (excepto el primero)
            team_list = [team_list[0]] + [team_list[-1]] + team_list[1:-1]
            
            # Emparejar equipos de esta ronda
            round_matches = []
            for i in range(n // 2):
                home = team_list[i]
                away = team_list[n - 1 - i]
                
                # Ignorar si uno es "bye"
                if home and away:
                    round_matches.append((home, away))
            
            # Repetir según número de vueltas
            for round_num in range(self.rounds):
                for match in round_matches:
                    matches.append({
                        'home': match[0],
                        'away': match[1],
                        'round': r + 1 + (round_num * num_rounds),
                    })
        
        return matches

    def _balance_schedule(self, matches):
        """
        Algoritmo de balanceo de calendario
        Solo juegos los fines de semana: sábado y domingo
        - Sábado: 2 juegos a las 9:30 y 12:00
        - Domingo: 2 juegos a las 9:30 y 12:00
        """
        balanced = []
        
        # Obtener fecha de inicio
        start_date = self.date_start or fields.Date.today()
        
        # Encontrar el primer sábado desde la fecha de inicio
        current_date = start_date
        while current_date.weekday() != 5:  # 5 = Sábado
            current_date += timedelta(days=1)
        
        # Horarios disponibles: 9:30 y 12:00
        # time_index 0 = 9:30, 1 = 12:00
        time_slots = [
            datetime.min.time().replace(hour=9, minute=30),
            datetime.min.time().replace(hour=12, minute=0),
        ]
        
        # Contadores para balanceo
        home_count = {team.id: 0 for team in self.team_ids}
        away_count = {team.id: 0 for team in self.team_ids}
        
        # Asignar fechas y horarios
        time_index = 0  # Empezar con el primer horario (9:30)
        
        for idx, match in enumerate(matches):
            # Determinar si es home o away basado en balanceo
            home_id = match['home'].id
            away_id = match['away'].id
            
            # Intercambiar si es necesario para balancear
            if home_count[home_id] > away_count[away_id] + 1:
                # Intercambiar
                match['home'], match['away'] = match['away'], match['home']
                home_id, away_id = away_id, home_id
            
            # Actualizar contadores
            home_count[home_id] += 1
            away_count[away_id] += 1
            
            # Asignar fecha y hora (hora fija sin conversión de timezone)
            # Crear string de fecha y hora directamente
            date_str = current_date.strftime('%Y-%m-%d')
            time_str = time_slots[time_index].strftime('%H:%M:%S')
            match['match_date'] = f"{date_str} {time_str}"
            
            balanced.append(match)
            
            # Avanzar al siguiente horario
            time_index += 1
            
            # Si ya usamos los 2 horarios del día, pasar al siguiente día
            if time_index >= len(time_slots):
                time_index = 0
                # Si es sábado (weekday 5), avanzar al domingo
                # Si es domingo (weekday 6), avanzar al siguiente sábado (6 días más)
                if current_date.weekday() == 5:  # 5 = Sábado
                    current_date += timedelta(days=1)  # Ir a domingo
                elif current_date.weekday() == 6:  # 6 = Domingo
                    current_date += timedelta(days=6)  # Ir al siguiente sábado (domingo + 6 = siguiente sábado)
        
        return balanced

    def _create_matches(self, matches_data, stage):
        """Crear registros de partidos"""
        Match = self.env['beiscool.match']
        
        for idx, match_data in enumerate(matches_data):
            Match.create({
                'name': f'Partido {idx + 1}',
                'copa_id': self.id,
                'home_team_id': match_data['home'].id,
                'away_team_id': match_data['away'].id,
                'match_date': match_data.get('match_date', False),
                'stage': stage,
                'sequence': idx + 1,
                'state': 'scheduled',
            })

    def _generate_semifinals(self):
        """Genera partidos de semifinal basados en la tabla de posiciones"""
        if not self.standings_ids or len(self.standings_ids) < 4:
            return
        
        # Obtener los 4 primeros equipos
        top_teams = self.standings_ids.sorted(
            key=lambda x: (x.matches_won, x.run_differential),
            reverse=True
        )[:4]
        
        Match = self.env['beiscool.match']
        
        # Semifinal 1: 1° vs 4°
        Match.create({
            'name': 'Semifinal 1',
            'copa_id': self.id,
            'home_team_id': top_teams[0].team_id.id,
            'away_team_id': top_teams[3].team_id.id,
            'stage': 'semifinal',
            'sequence': len(self.match_ids) + 1,
            'state': 'scheduled',
        })
        
        # Semifinal 2: 2° vs 3°
        Match.create({
            'name': 'Semifinal 2',
            'copa_id': self.id,
            'home_team_id': top_teams[1].team_id.id,
            'away_team_id': top_teams[2].team_id.id,
            'stage': 'semifinal',
            'sequence': len(self.match_ids) + 2,
            'state': 'scheduled',
        })

    def _generate_final(self):
        """Genera el partido final"""
        semifinals = self.match_ids.filtered(lambda m: m.stage == 'semifinal' and m.state == 'played')
        
        if len(semifinals) < 2:
            return
        
        winners = semifinals.mapped('winner_id')
        
        if len(winners) < 2:
            return
        
        Match = self.env['beiscool.match']
        
        Match.create({
            'name': 'Final',
            'copa_id': self.id,
            'home_team_id': winners[0].id,
            'away_team_id': winners[1].id,
            'stage': 'final',
            'sequence': len(self.match_ids) + 1,
            'state': 'scheduled',
        })

    # ============================================
    # TABLA DE POSICIONES
    # ============================================

    def _compute_standings(self):
        """Calcula y actualiza la tabla de posiciones"""
        self.ensure_one()
        
        # Eliminar standings existentes
        self.standings_ids.unlink()
        
        Standings = self.env['beiscool.standings']
        
        # Obtener equipos
        teams = self.team_ids
        
        # Obtener partidos jugados (solo round-robin)
        matches = self.match_ids.filtered(
            lambda m: m.stage == 'round_robin' and m.state == 'played'
        )
        
        for team in teams:
            # Partidos jugados como local
            home_matches = matches.filtered(lambda m: m.home_team_id == team)
            # Partidos jugados como visitante
            away_matches = matches.filtered(lambda m: m.away_team_id == team)
            
            # Total partidos jugados
            total_matches = len(home_matches) + len(away_matches)
            
            # Partidos ganados
            home_wins = len(home_matches.filtered(lambda m: m.winner_id == team))
            away_wins = len(away_matches.filtered(lambda m: m.winner_id == team))
            matches_won = home_wins + away_wins
            
            # Partidos perdidos
            matches_lost = total_matches - matches_won
            
            # Carreras anotadas (como local)
            runs_scored_home = sum(home_matches.mapped('home_runs'))
            # Carreras anotadas (como visitante)
            runs_scored_away = sum(away_matches.mapped('away_runs'))
            runs_scored = runs_scored_home + runs_scored_away
            
            # Carreras permitidas (como local)
            runs_allowed_home = sum(home_matches.mapped('away_runs'))
            # Carreras permitidas (como visitante)
            runs_allowed_away = sum(away_matches.mapped('home_runs'))
            runs_allowed = runs_allowed_home + runs_allowed_away
            
            # Diferencia de carreras
            run_differential = runs_scored - runs_allowed
            
            # Puntos (3 por victoria, 0 por derrota)
            points = matches_won * 3
            
            Standings.create({
                'copa_id': self.id,
                'team_id': team.id,
                'matches_played': total_matches,
                'matches_won': matches_won,
                'matches_lost': matches_lost,
                'runs_scored': runs_scored,
                'runs_allowed': runs_allowed,
                'run_differential': run_differential,
                'points': points,
            })
        
        return True
