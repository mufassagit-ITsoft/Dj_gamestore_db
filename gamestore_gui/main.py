import tkinter as tk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Allow imports from project root
from config import COLORS, FONTS, WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH, DB_PATH
from widgets.sidebar import Sidebar

# Views
from views import (
    DashboardView, 
    ProductsView, 
    OrdersView, 
    RefundsView, 
    RewardsView, 
    UsersView
)

import database as db


VIEW_MAP = {
    'dashboard': DashboardView,
    'products':  ProductsView,
    'orders':    OrdersView,
    'refunds':   RefundsView,
    'rewards':   RewardsView,
    'users':     UsersView,
}


class DatastoreApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Gamestore Datastore')
        self.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
        self.minsize(900, 600)
        self.configure(bg=COLORS['sidebar_bg'])

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - WINDOW_WIDTH)  // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f'+{x}+{y}')

        self._check_db()
        self._build()
        self._navigate('dashboard')

    def _check_db(self):
        """Warn the user if the database file is missing."""
        if not db.db_exists():
            messagebox.showwarning(
                'Database Not Found',
                f'Could not find the database file at:\n\n{DB_PATH}\n\n'
                'Please update DB_PATH in config.py to point to your '
                'separate_db.sqlite3 file, then restart the app.'
            )

    def _build(self):
        # Sidebar
        self.sidebar = Sidebar(self, on_navigate=self._navigate)
        self.sidebar.pack(side='left', fill='y')

        # Thin separator
        tk.Frame(self, bg=COLORS['card_border'], width=1).pack(side='left', fill='y')

        # Main content area
        self.content_frame = tk.Frame(self, bg=COLORS['bg'])
        self.content_frame.pack(side='left', fill='both', expand=True)

        # Top bar
        self._build_topbar()

        # View container
        self.view_container = tk.Frame(self.content_frame, bg=COLORS['bg'])
        self.view_container.pack(fill='both', expand=True)

        self.current_view = None

    def _build_topbar(self):
        topbar = tk.Frame(self.content_frame, bg=COLORS['card_bg'], height=48)
        topbar.pack(fill='x')
        topbar.pack_propagate(False)

        tk.Frame(topbar, bg=COLORS['card_border'], height=1).pack(
            side='bottom', fill='x'
        )

        # DB path indicator
        db_text = f'DB: {DB_PATH.name}  •  {"✓ Connected" if db.db_exists() else "✗ Not found"}'
        color = COLORS['success'] if db.db_exists() else COLORS['danger']

        tk.Label(
            topbar,
            text=db_text,
            font=FONTS['small'],
            bg=COLORS['card_bg'],
            fg=color,
        ).pack(side='left', padx=20)

        # Refresh button
        refresh_btn = tk.Button(
            topbar,
            text='↻  Refresh',
            font=FONTS['body_bold'],
            bg=COLORS['primary'],
            fg='#ffffff',
            relief='flat',
            padx=14, pady=4,
            cursor='hand2',
            command=self._refresh_view,
        )
        refresh_btn.pack(side='right', padx=16, pady=8)

        # DB path (full)
        tk.Label(
            topbar,
            text=str(DB_PATH),
            font=FONTS['small'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_muted'],
        ).pack(side='right', padx=(0, 8))

    def _navigate(self, key):
        """Switch to the view for the given key."""
        self.sidebar.set_active(key)

        # Destroy current view
        for widget in self.view_container.winfo_children():
            widget.destroy()

        # Instantiate and show new view
        ViewClass = VIEW_MAP.get(key)
        if ViewClass:
            view = ViewClass(self.view_container)
            view.pack(fill='both', expand=True)
            self.current_view = view

    def _refresh_view(self):
        """Re-navigate to the current view to reload data."""
        if self.sidebar.active_key:
            self._navigate(self.sidebar.active_key)


def main():
    app = DatastoreApp()
    app.mainloop()


if __name__ == '__main__':
    main()