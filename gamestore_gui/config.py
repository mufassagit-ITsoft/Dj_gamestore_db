import os
from pathlib import Path

DB_PATH = Path('/home/mufassa/Documents/Compfiles/python/Django/gamestore_db/separate_db.sqlite3')

if os.environ.get('DATASTORE_DB_PATH'):
    DB_PATH = Path(os.environ['DATASTORE_DB_PATH'])

COLORS = {
    # Sidebar
    'sidebar_bg':        '#1a1d2e',
    'sidebar_hover':     '#2d3154',
    'sidebar_active':    '#4a5568',
    'sidebar_text':      '#a0aec0',
    'sidebar_text_active': '#ffffff',
    'sidebar_accent':    '#6c63ff',

    # Main content
    'bg':                '#f0f2f5',
    'card_bg':           '#ffffff',
    'card_border':       '#e2e8f0',

    # Text
    'text_primary':      '#1a202c',
    'text_secondary':    '#718096',
    'text_muted':        '#a0aec0',

    # Status / accent
    'primary':           '#6c63ff',
    'success':           '#38a169',
    'warning':           '#d69e2e',
    'danger':            '#e53e3e',
    'info':              '#3182ce',

    # Table
    'table_header':      '#2d3748',
    'table_row_odd':     '#ffffff',
    'table_row_even':    '#f7fafc',
    'table_select':      '#ebf4ff',
    'table_select_fg':   '#2b6cb0',

    # Input
    'input_bg':          '#ffffff',
    'input_border':      '#cbd5e0',
    'input_focus':       '#6c63ff',
}

FONTS = {
    'heading':      ('Segoe UI', 20, 'bold'),
    'subheading':   ('Segoe UI', 14, 'bold'),
    'body':         ('Segoe UI', 10),
    'body_bold':    ('Segoe UI', 10, 'bold'),
    'small':        ('Segoe UI', 9),
    'small_bold':   ('Segoe UI', 9, 'bold'),
    'sidebar_nav':  ('Segoe UI', 11),
    'sidebar_title':('Segoe UI', 13, 'bold'),
    'stat_number':  ('Segoe UI', 28, 'bold'),
    'stat_label':   ('Segoe UI', 10),
    'mono':         ('Courier New', 9),
}

WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 800
SIDEBAR_WIDTH = 220

ROW_HEIGHT = 28