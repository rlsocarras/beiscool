# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class BeiscoolWebsite(http.Controller):
    """Controlador para páginas públicas del módulo beiscool"""

    @http.route('/copa/<int:copa_id>', type='http', auth='public', website=True)
    def copa_page(self, copa_id):
        """Página pública de una copa de béisbol"""
        copa = request.env['beiscool.copa'].sudo().browse(copa_id)
        if not copa.exists():
            return request.not_found()
        
        # Obtener equipos con su información
        teams = copa.team_ids.sorted('name')
        
        # Obtener tabla de posiciones
        standings = copa.standings_ids.sorted('position')
        
        # Obtener árbitros
        referees = copa.referee_ids.sorted('name')
        
        # Obtener próximos partidos
        upcoming_matches = copa.match_ids.filtered(
            lambda m: m.state == 'scheduled' and m.match_date
        ).sorted('match_date')[:5]
        
        # Obtener últimos partidos jugados
        past_matches = copa.match_ids.filtered(
            lambda m: m.state == 'played' and m.match_date
        ).sorted('match_date', reverse=True)[:5]
        
        # Obtener todos los partidos para el calendario
        all_matches = copa.match_ids.filtered(
            lambda m: m.match_date
        ).sorted('match_date')
        
        values = {
            'copa': copa,
            'teams': teams,
            'standings': standings,
            'referees': referees,
            'upcoming_matches': upcoming_matches,
            'past_matches': past_matches,
            'all_matches': all_matches,
        }
        
        return request.render('beiscool.copa_page', values)

    @http.route('/equipo/<int:team_id>', type='http', auth='public', website=True)
    def team_page(self, team_id):
        """Página pública de un equipo de béisbol"""
        team = request.env['beiscool.team'].sudo().browse(team_id)
        if not team.exists():
            return request.not_found()
        
        # Obtener la copa asociada
        copa = team.copa_id
        
        # Forzar la carga de campos relacionados
        team = request.env['beiscool.team'].sudo().search([('id', '=', team_id)])
        team = team[0] if team else False
        
        if not team:
            return request.not_found()
        
        # Obtener partidos del equipo
        matches = Copa = request.env['beiscool.match'].sudo().search([
            '|',
            ('home_team_id', '=', team.id),
            ('away_team_id', '=', team.id),
            ('copa_id', '=', copa.id) if copa else (0, '=', 0),
        ])
        
        past_matches = matches.filtered(lambda m: m.state == 'played' and m.match_date).sorted('match_date', reverse=True)
        upcoming_matches = matches.filtered(lambda m: m.state == 'scheduled' and m.match_date).sorted('match_date')
        
        # Obtener jugadores
        players = team.player_ids.sorted('name')
        
        # Obtener estadísticas del equipo en la copa
        standings = False
        if copa:
            standings = copa.standings_ids.filtered(lambda s: s.team_id == team)
        
        values = {
            'team': team,
            'copa': copa,
            'players': players,
            'past_matches': past_matches,
            'upcoming_matches': upcoming_matches,
            'standings': standings,
        }
        
        return request.render('beiscool.team_page', values)

    @http.route('/copas', type='http', auth='public', website=True)
    def copas_list(self):
        """Página con lista de todas las copas"""
        copas = request.env['beiscool.copa'].sudo().search([])
        
        values = {
            'copas': copas,
        }
        
        return request.render('beiscool.copas_list_page', values)
