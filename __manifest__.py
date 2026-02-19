# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Copas de Béisbol',
    'category': 'Sports',
    'version': '1.0',
    'summary': 'Módulo para gestionar copas y torneos de béisbol',
    'description': """
        Módulo para la gestión integral de copas y torneos de béisbol.
        
        Características:
        - Gestión de múltiples copas de béisbol
        - Registro de equipos, jugadores y árbitros
        - Generación automática de calendario (round-robin)
        - Tabla de posiciones automática
        - Semifinal y final automáticas
        - Integración con calendario de Odoo
        - Páginas públicas web estilo béisbol
    """,
    'author': 'Robert LS',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'calendar', 'website'],
    'data': [
        'security/beiscool_security.xml',
        'security/ir.model.access.csv',
        # Las vistas deben cargarse antes que el menú para que las acciones existan
        'views/copa_views.xml',
        'views/player_views.xml',
        'views/team_views.xml',
        'views/match_views.xml',
        'views/referee_views.xml',
        'views/standings_views.xml',
        'views/beiscool_menu.xml',
        # Plantillas QWeb para páginas públicas
        'static/src/xml/copa_page.xml',
    ],
    'demo': [
        'demo/cup_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
