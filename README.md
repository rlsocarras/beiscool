# Gestión de Copas de Béisbol - Beiscool

Módulo para Odoo 18 que permite gestionar copas y torneos de béisbol.

## Características

### Gestión de Copas
- Crear y administrar múltiples copas de béisbol
- Configurar número de vueltas (round-robin)
- Configurar fases de semifinal y final

### Gestión de Equipos y Jugadores
- Registro de equipos con imagen y capitán
- Registro de jugadores con información de contacto e imagen
- Asignar jugadores a equipos

### Calendario Automático
- Generación automática de calendario round-robin
- Balanceo de calendario considerando:
  - Distribución local/visitante
  - Días de la semana
  - Horarios de partidos
- Generación automática de semifinal y final

### Tabla de Posiciones
- Actualización automática de estadísticas
- Ordenamiento por:
  1. Partidos ganados (descendente)
  2. Diferencia de carreras (descendente)
  3. Carreras anotadas (descendente)
- Criterios de desempate por encuentro directo

### Integración
- Vistas de calendario para partidos
- Vistas kanban para copas

## Instalación

1. Copiar el directorio `beiscool` a la carpeta `addons` de Odoo
2. Actualizar la lista de aplicaciones
3. Buscar "Gestión de Béisbol" e instalar

## Uso

1. Crear una nueva Copa
2. Agregar equipos a la copa
3. Generar el calendario
4. Registrar los resultados de los partidos
5. Consultar la tabla de posiciones

## Modelos

- **Copa**: Torneos de béisbol
- **Equipo**: Equipos participantes
- **Jugador**: Jugadores registrados
- **Partido**: Encuentros entre equipos
- **Árbitro**: Árbitros del torneo
- **Standings**: Tabla de posiciones

## Requisitos

- Odoo 18
- Módulo base (base)
- Módulo calendario (calendar)

## Licencia

LGPL-3
