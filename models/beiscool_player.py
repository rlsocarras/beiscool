# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BeiscoolPlayer(models.Model):
    _name = 'beiscool.player'
    _description = 'Jugador de Béisbol'
    _order = 'name'

    name = fields.Char(
        string='Nombre',
        required=True,
        size=200,
    )

    contact = fields.Char(
        string='Contacto',
        size=100,
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

    team_ids = fields.Many2many(
        'beiscool.team',
        'beiscool_team_player_rel',
        'player_id',
        'team_id',
        string='Equipos',
    )

    is_captain = fields.Boolean(
        string='Es Capitán',
        default=False,
    )

    email = fields.Char(
        string='Correo Electrónico',
        size=200,
    )

    phone = fields.Char(
        string='Teléfono',
        size=20,
    )

    # Información adicional
    birth_date = fields.Date(
        string='Fecha de Nacimiento',
    )

    position = fields.Char(
        string='Posición',
        size=50,
    )

    number = fields.Integer(
        string='Número de Camiseta',
    )

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name
