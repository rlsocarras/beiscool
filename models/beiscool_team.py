# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BeiscoolTeam(models.Model):
    _name = 'beiscool.team'
    _description = 'Equipo de Béisbol'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        size=200,
    )

    image = fields.Binary(
        string='Imagen',
        attachment=True,
    )

    image_medium = fields.Binary(
        string='Imagen Mediana',
        attachment=True,
        related='image',
    )

    player_quantity = fields.Integer(
        string='Cantidad de Jugadores',
        compute='_compute_player_quantity',
        store=True,
    )

    player_ids = fields.Many2many(
        'beiscool.player',
        'beiscool_team_player_rel',
        'team_id',
        'player_id',
        string='Jugadores',
    )

    captain_id = fields.Many2one(
        'beiscool.player',
        string='Capitán',
        domain="[('id', 'in', player_ids)]",
    )

    copa_id = fields.Many2one(
        'beiscool.copa',
        string='Copa',
        ondelete='cascade',
    )

    color = fields.Integer(
        string='Color',
        default=0,
    )

    # Campos calculados
    matches_played = fields.Integer(
        string='Partidos Jugados',
        compute='_compute_team_stats',
        store=True,
    )

    matches_won = fields.Integer(
        string='Partidos Ganados',
        compute='_compute_team_stats',
        store=False,
    )

    @api.depends('player_ids')
    def _compute_player_quantity(self):
        for record in self:
            record.player_quantity = len(record.player_ids)

    @api.depends('copa_id', 'copa_id.match_ids')
    def _compute_team_stats(self):
        for record in self:
            if not record.copa_id:
                record.matches_played = 0
                record.matches_won = 0
                continue
            
            matches = record.copa_id.match_ids.filtered(
                lambda m: (m.home_team_id == record or m.away_team_id == record) 
                and m.state == 'played'
            )
            
            record.matches_played = len(matches)
            record.matches_won = len(matches.filtered(lambda m: m.winner_id == record))

    def get_players_list(self):
        """Retorna lista de nombres de jugadores"""
        return ', '.join(self.player_ids.mapped('name'))
