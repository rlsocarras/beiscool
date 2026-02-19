# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BeiscoolReferee(models.Model):
    _name = 'beiscool.referee'
    _description = 'Árbitro de Béisbol'
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

    certification = fields.Char(
        string='Certificación',
        size=200,
    )

    image = fields.Binary(
        string='Foto',
        attachment=True,
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
    experience_years = fields.Integer(
        string='Años de Experiencia',
        default=0,
    )

    level = fields.Selection(
        [
            ('local', 'Local'),
            ('regional', 'Regional'),
            ('national', 'Nacional'),
            ('international', 'Internacional'),
        ],
        string='Nivel',
        default='local',
    )

    is_active = fields.Boolean(
        string='Activo',
        default=True,
    )
