import tkinter as tk
from config import COLORS, FONTS, SIDEBAR_WIDTH


NAV_ITEMS = [
    ('dashboard',  '🏠',  'Dashboard'),
    ('products',   '🎮',  'Products'),
    ('orders',     '🛒',  'Orders'),
    ('refunds',    '🔄',  'Refunds'),
    ('rewards',    '⭐',  'Rewards'),
    ('users',      '👥',  'Users'),
]


class Sidebar(tk.Frame):
    def __init__(self, parent, on_navigate, **kwargs):
        super().__init__(
            parent,
            bg=COLORS['sidebar_bg'],
            width=SIDEBAR_WIDTH,
            **kwargs
        )
        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.active_key = 'dashboard'
        self.buttons = {}
        self._build()

    def _build(self):
        # App title
        title_frame = tk.Frame(self, bg=COLORS['sidebar_bg'])
        title_frame.pack(fill='x', pady=(24, 4), padx=16)

        tk.Label(
            title_frame,
            text='📦',
            font=('Segoe UI', 22),
            bg=COLORS['sidebar_bg'],
            fg=COLORS['sidebar_accent'],
        ).pack(side='left')

        tk.Label(
            title_frame,
            text='  Datastore',
            font=FONTS['sidebar_title'],
            bg=COLORS['sidebar_bg'],
            fg='#ffffff',
        ).pack(side='left')

        # Divider
        tk.Frame(self, bg=COLORS['sidebar_active'], height=1).pack(
            fill='x', padx=16, pady=(8, 16)
        )

        # Nav label
        tk.Label(
            self,
            text='NAVIGATION',
            font=('Segoe UI', 8, 'bold'),
            bg=COLORS['sidebar_bg'],
            fg=COLORS['text_muted'],
        ).pack(anchor='w', padx=20, pady=(0, 8))

        # Nav buttons
        for key, icon, label in NAV_ITEMS:
            btn = self._make_nav_button(key, icon, label)
            self.buttons[key] = btn

        # Version label at bottom
        tk.Label(
            self,
            text='Gamestore Datastore v1.0',
            font=FONTS['small'],
            bg=COLORS['sidebar_bg'],
            fg=COLORS['text_muted'],
        ).pack(side='bottom', pady=16)

    def _make_nav_button(self, key, icon, label):
        frame = tk.Frame(self, bg=COLORS['sidebar_bg'], cursor='hand2')
        frame.pack(fill='x', padx=10, pady=2)

        inner = tk.Frame(frame, bg=COLORS['sidebar_bg'], cursor='hand2')
        inner.pack(fill='x', ipady=8, ipadx=10)

        icon_label = tk.Label(
            inner,
            text=icon,
            font=('Segoe UI', 13),
            bg=COLORS['sidebar_bg'],
            fg=COLORS['sidebar_text'],
            width=2,
        )
        icon_label.pack(side='left', padx=(4, 6))

        text_label = tk.Label(
            inner,
            text=label,
            font=FONTS['sidebar_nav'],
            bg=COLORS['sidebar_bg'],
            fg=COLORS['sidebar_text'],
            anchor='w',
        )
        text_label.pack(side='left', fill='x', expand=True)

        # Bind click and hover to all parts
        for widget in (frame, inner, icon_label, text_label):
            widget.bind('<Button-1>', lambda e, k=key: self._navigate(k))
            widget.bind('<Enter>', lambda e, f=inner, il=icon_label, tl=text_label, k=key:
                        self._on_hover(f, il, tl, k))
            widget.bind('<Leave>', lambda e, f=inner, il=icon_label, tl=text_label, k=key:
                        self._on_leave(f, il, tl, k))

        return {'frame': frame, 'inner': inner,
                'icon': icon_label, 'text': text_label}

    def _navigate(self, key):
        self.set_active(key)
        self.on_navigate(key)

    def set_active(self, key):
        # Reset previous active
        if self.active_key in self.buttons:
            prev = self.buttons[self.active_key]
            for w in (prev['inner'], prev['icon'], prev['text']):
                w.config(bg=COLORS['sidebar_bg'])
            prev['icon'].config(fg=COLORS['sidebar_text'])
            prev['text'].config(fg=COLORS['sidebar_text'])

        # Set new active
        self.active_key = key
        if key in self.buttons:
            curr = self.buttons[key]
            for w in (curr['inner'], curr['icon'], curr['text']):
                w.config(bg=COLORS['sidebar_active'])
            curr['icon'].config(fg='#ffffff')
            curr['text'].config(fg='#ffffff', font=FONTS['body_bold'])

    def _on_hover(self, inner, icon_lbl, text_lbl, key):
        if key != self.active_key:
            inner.config(bg=COLORS['sidebar_hover'])
            icon_lbl.config(bg=COLORS['sidebar_hover'])
            text_lbl.config(bg=COLORS['sidebar_hover'])

    def _on_leave(self, inner, icon_lbl, text_lbl, key):
        if key != self.active_key:
            inner.config(bg=COLORS['sidebar_bg'])
            icon_lbl.config(bg=COLORS['sidebar_bg'])
            text_lbl.config(bg=COLORS['sidebar_bg'])