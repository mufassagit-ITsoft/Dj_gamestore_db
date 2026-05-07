import database as db
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from widgets.data_table import DataTable

# base view
class BaseView(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)

    def make_header(self, title, subtitle=''):
        """Page title + optional subtitle row."""
        frame = tk.Frame(self, bg=COLORS['bg'])
        frame.pack(fill='x', padx=28, pady=(24, 0))

        tk.Label(
            frame, text=title,
            font=FONTS['heading'],
            bg=COLORS['bg'],
            fg=COLORS['text_primary'],
        ).pack(side='left')

        if subtitle:
            tk.Label(
                frame, text=f'  {subtitle}',
                font=FONTS['body'],
                bg=COLORS['bg'],
                fg=COLORS['text_secondary'],
            ).pack(side='left', pady=(6, 0))

        # Horizontal rule
        tk.Frame(self, bg=COLORS['card_border'], height=1).pack(
            fill='x', padx=28, pady=(10, 16)
        )

        return frame

    def make_search_bar(self, parent, placeholder, on_search, width=30):
        """Search entry with icon and real-time callback."""
        frame = tk.Frame(parent, bg=COLORS['bg'])

        tk.Label(
            frame, text='🔍',
            font=FONTS['body'],
            bg=COLORS['bg'],
            fg=COLORS['text_secondary'],
        ).pack(side='left', padx=(0, 4))

        var = tk.StringVar()
        entry = tk.Entry(
            frame,
            textvariable=var,
            font=FONTS['body'],
            bg=COLORS['input_bg'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['primary'],
            relief='flat',
            bd=0,
            width=width,
            highlightthickness=1,
            highlightbackground=COLORS['input_border'],
            highlightcolor=COLORS['primary'],
        )
        entry.pack(side='left', ipady=6, ipadx=8)

        # Placeholder
        entry.insert(0, placeholder)
        entry.config(fg=COLORS['text_muted'])

        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, 'end')
                entry.config(fg=COLORS['text_primary'])

        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=COLORS['text_muted'])

        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        var.trace_add('write', lambda *a: on_search(
            '' if entry.get() == placeholder else entry.get()
        ))

        return frame, entry, var

    def make_stat_card(self, parent, label, value, color, icon=''):
        """A colored summary card with a big number."""
        card = tk.Frame(
            parent,
            bg=COLORS['card_bg'],
            highlightthickness=1,
            highlightbackground=COLORS['card_border'],
        )

        # Color accent bar on left
        tk.Frame(card, bg=color, width=5).pack(side='left', fill='y')

        inner = tk.Frame(card, bg=COLORS['card_bg'])
        inner.pack(side='left', padx=16, pady=14, fill='both', expand=True)

        tk.Label(
            inner,
            text=f'{icon}  {label}' if icon else label,
            font=FONTS['stat_label'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
        ).pack(anchor='w')

        tk.Label(
            inner,
            text=str(value),
            font=FONTS['stat_number'],
            bg=COLORS['card_bg'],
            fg=color,
        ).pack(anchor='w')

        return card

    def make_card(self, parent, **kwargs):
        """A plain white card container."""
        return tk.Frame(
            parent,
            bg=COLORS['card_bg'],
            highlightthickness=1,
            highlightbackground=COLORS['card_border'],
            **kwargs
        )

    def make_label_value(self, parent, label, value, row):
        """A label+value pair in a grid layout."""
        tk.Label(
            parent,
            text=label + ':',
            font=FONTS['body_bold'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='e',
        ).grid(row=row, column=0, sticky='e', padx=(12, 8), pady=4)

        tk.Label(
            parent,
            text=str(value) if value is not None else '—',
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            anchor='w',
            wraplength=300,
        ).grid(row=row, column=1, sticky='w', pady=4)

    def make_section_label(self, parent, text):
        """A bold section divider label."""
        tk.Label(
            parent,
            text=text,
            font=FONTS['subheading'],
            bg=COLORS['bg'],
            fg=COLORS['text_primary'],
        ).pack(anchor='w', padx=28, pady=(16, 4))

    def make_count_badge(self, parent, count):
        """Small count badge next to a heading."""
        return tk.Label(
            parent,
            text=f' {count} records ',
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='#ffffff',
            padx=6, pady=2,
        )
    
'''
dashboard view

Dashboard landing page — stat cards, recent orders, recent products.
'''

class DashboardView(BaseView):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.make_header('Dashboard', 'Overview of synced Gamestore data')

        # Scrollable content
        canvas = tk.Canvas(self, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        self.content = tk.Frame(canvas, bg=COLORS['bg'])
        self.window = canvas.create_window((0, 0), window=self.content, anchor='nw')

        self.content.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox('all')
        ))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(
            self.window, width=e.width
        ))

        self.refresh()

    def refresh(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        stats = db.get_dashboard_stats()

        # ── Stat Cards ─────────────────────────────────────────
        cards_frame = tk.Frame(self.content, bg=COLORS['bg'])
        cards_frame.pack(fill='x', padx=28, pady=(0, 20))

        card_data = [
            ('Products',       stats['products'],       COLORS['primary'], '🎮'),
            ('Orders',         stats['orders'],         COLORS['success'], '🛒'),
            ('Refund Requests',stats['refunds'],        COLORS['warning'], '🔄'),
            ('Reward Accounts',stats['reward_accounts'],COLORS['info'],    '⭐'),
        ]

        for i, (label, value, color, icon) in enumerate(card_data):
            card = self.make_stat_card(cards_frame, label, value, color, icon)
            card.grid(row=0, column=i, sticky='nsew', padx=(0, 12), ipady=4)
            cards_frame.columnconfigure(i, weight=1)

        # ── Second row cards ───────────────────────────────────
        cards2 = tk.Frame(self.content, bg=COLORS['bg'])
        cards2.pack(fill='x', padx=28, pady=(0, 24))

        card_data2 = [
            ('Total Revenue',  f"${stats['total_revenue']:,.2f}", COLORS['success'], '💰'),
            ('Users',          stats['users'],                    COLORS['primary'], '👥'),
            ('Categories',     stats['categories'],               COLORS['info'],    '📂'),
            ('Topics',         stats['topics'],                   COLORS['warning'], '🏷️'),
        ]

        for i, (label, value, color, icon) in enumerate(card_data2):
            card = self.make_stat_card(cards2, label, value, color, icon)
            card.grid(row=0, column=i, sticky='nsew', padx=(0, 12), ipady=4)
            cards2.columnconfigure(i, weight=1)

        # ── Tables row ─────────────────────────────────────────
        tables_row = tk.Frame(self.content, bg=COLORS['bg'])
        tables_row.pack(fill='both', padx=28, pady=(0, 24), expand=True)
        tables_row.columnconfigure(0, weight=3)
        tables_row.columnconfigure(1, weight=2)

        # Recent Orders table
        orders_card = self.make_card(tables_row)
        orders_card.grid(row=0, column=0, sticky='nsew', padx=(0, 12))

        tk.Label(
            orders_card,
            text='🛒  Recent Orders',
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            anchor='w',
        ).pack(anchor='w', padx=16, pady=(14, 8))

        tk.Frame(orders_card, bg=COLORS['card_border'], height=1).pack(fill='x')

        order_table = DataTable(
            orders_card,
            columns=[
                ('id',     '#',       50,  'center'),
                ('name',   'Name',    160, 'w'),
                ('email',  'Email',   180, 'w'),
                ('amount', 'Amount',  80,  'e'),
                ('date',   'Date',    120, 'center'),
            ],
        )
        order_table.pack(fill='both', expand=True, padx=8, pady=8)

        recent_orders = db.get_recent_orders(10)
        order_table.load([
            (r['id'], r['full_name'], r['email'],
             f"${r['amount_paid']}", str(r['date_ordered'])[:10])
            for r in recent_orders
        ])

        # Recent Products table
        products_card = self.make_card(tables_row)
        products_card.grid(row=0, column=1, sticky='nsew')

        tk.Label(
            products_card,
            text='🎮  Recent Products',
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
            anchor='w',
        ).pack(anchor='w', padx=16, pady=(14, 8))

        tk.Frame(products_card, bg=COLORS['card_border'], height=1).pack(fill='x')

        product_table = DataTable(
            products_card,
            columns=[
                ('title', 'Title',  170, 'w'),
                ('price', 'Price',   70, 'e'),
                ('stock', 'Stock',   60, 'center'),
            ],
        )
        product_table.pack(fill='both', expand=True, padx=8, pady=8)

        recent_products = db.get_recent_products(8)
        product_table.load([
            (r['title'], f"${r['price']}", r['quantity_available'])
            for r in recent_products
        ])

'''
order view - Orders list with search and an order item sub-table 
on row selection.

'''

class OrdersView(BaseView):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.make_header('🛒  Orders', 'All synced orders from Gamestore')

        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS['bg'])
        toolbar.pack(fill='x', padx=28, pady=(0, 12))

        search_frame, self.search_entry, _ = self.make_search_bar(
            toolbar, 'Search by name or email...', self._on_search, width=32
        )
        search_frame.pack(side='left')

        self.count_label = tk.Label(
            toolbar, text='',
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='#ffffff',
            padx=8, pady=3,
        )
        self.count_label.pack(side='right')

        paned = tk.PanedWindow(self, orient='vertical', bg=COLORS['bg'],
                               sashrelief='flat', sashwidth=6)
        paned.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        # Orders table card
        orders_card = self.make_card(paned)
        self.orders_table = DataTable(
            orders_card,
            columns=[
                ('id',     '#',        50,  'center'),
                ('name',   'Customer', 180, 'w'),
                ('email',  'Email',    200, 'w'),
                ('user',   'Username', 120, 'w'),
                ('amount', 'Amount',   90,  'e'),
                ('items',  'Items',    55,  'center'),
                ('date',   'Date',     130, 'center'),
            ],
            on_select=self._on_order_select,
        )
        self.orders_table.pack(fill='both', expand=True, padx=8, pady=8)
        paned.add(orders_card, minsize=200)

        # Order items card
        items_card = self.make_card(paned)

        self.items_header = tk.Label(
            items_card,
            text='Order Items  —  select an order above',
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w',
        )
        self.items_header.pack(anchor='w', padx=16, pady=(12, 6))
        tk.Frame(items_card, bg=COLORS['card_border'], height=1).pack(fill='x')

        self.items_table = DataTable(
            items_card,
            columns=[
                ('id',       '#',        50,  'center'),
                ('product',  'Product',  220, 'w'),
                ('brand',    'Brand',    130, 'w'),
                ('qty',      'Qty',      55,  'center'),
                ('price',    'Price',    80,  'e'),
                ('subtotal', 'Subtotal', 90,  'e'),
            ],
        )
        self.items_table.pack(fill='both', expand=True, padx=8, pady=8)
        paned.add(items_card, minsize=150)

        self.load_orders()

    def load_orders(self, search=''):
        rows = db.get_orders(search=search)
        self.orders_table.load([
            (r['id'], r['full_name'], r['email'],
             r['username'] or 'Guest',
             f"${r['amount_paid']}", r['item_count'],
             str(r['date_ordered'])[:16])
            for r in rows
        ])
        self.count_label.config(text=f' {self.orders_table.row_count()} orders ')

    def _on_search(self, text):
        self.load_orders(search=text)

    def _on_order_select(self, values):
        order_id = values[0]
        order = db.get_order_detail(order_id)
        if order:
            self.items_header.config(
                text=f'Order Items  —  Order #{order_id}  •  {order["full_name"]}  •  ${order["amount_paid"]}',
                fg=COLORS['text_primary'],
            )

        items = db.get_order_items(order_id)
        self.items_table.load([
            (r['id'], r['title'] or '—', r['brand'] or '—',
             r['quantity'], f"${r['price']}", f"${r['subtotal']}")
            for r in items
        ])

'''
product views - Products list with search, category filter, and 
a detail panel.

'''

class ProductsView(BaseView):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.make_header('🎮  Products', 'All synced products from Gamestore')

        # ── Toolbar ────────────────────────────────────────────
        toolbar = tk.Frame(self, bg=COLORS['bg'])
        toolbar.pack(fill='x', padx=28, pady=(0, 12))

        search_frame, self.search_entry, self.search_var = self.make_search_bar(
            toolbar, 'Search by title or brand...', self._on_search, width=32
        )
        search_frame.pack(side='left', padx=(0, 16))

        # Category filter
        tk.Label(
            toolbar, text='Category:',
            font=FONTS['body'],
            bg=COLORS['bg'],
            fg=COLORS['text_secondary'],
        ).pack(side='left', padx=(0, 6))

        self.category_var = tk.StringVar(value='All')
        self.categories = [('', 'All')] + [(str(r['id']), r['name']) for r in db.get_categories()]
        category_names = [c[1] for c in self.categories]

        self.category_combo = ttk.Combobox(
            toolbar,
            textvariable=self.category_var,
            values=category_names,
            state='readonly',
            width=20,
            font=FONTS['body'],
        )
        self.category_combo.pack(side='left')
        self.category_combo.bind('<<ComboboxSelected>>', self._on_filter_change)

        # Record count badge
        self.count_label = tk.Label(
            toolbar,
            text='',
            font=FONTS['small'],
            bg=COLORS['primary'],
            fg='#ffffff',
            padx=8, pady=3,
        )
        self.count_label.pack(side='right')

        # ── Main split: table | detail ──────────────────────────
        split = tk.Frame(self, bg=COLORS['bg'])
        split.pack(fill='both', expand=True, padx=28, pady=(0, 16))
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=1)
        split.rowconfigure(0, weight=1)

        # Table card
        table_card = self.make_card(split)
        table_card.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        table_card.rowconfigure(0, weight=1)
        table_card.columnconfigure(0, weight=1)

        self.table = DataTable(
            table_card,
            columns=[
                ('id',       'ID',       45,  'center'),
                ('title',    'Title',    200, 'w'),
                ('brand',    'Brand',    110, 'w'),
                ('category', 'Category', 120, 'w'),
                ('price',    'Price',    70,  'e'),
                ('stock',    'Stock',    60,  'center'),
                ('sold',     'Sold',     55,  'center'),
                ('revenue',  'Revenue',  90,  'e'),
            ],
            on_select=self._on_row_select,
        )
        self.table.pack(fill='both', expand=True, padx=8, pady=8)

        # Detail panel card
        self.detail_card = self.make_card(split)
        self.detail_card.grid(row=0, column=1, sticky='nsew')

        tk.Label(
            self.detail_card,
            text='Product Detail',
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_primary'],
        ).pack(anchor='w', padx=14, pady=(14, 4))
        tk.Frame(self.detail_card, bg=COLORS['card_border'], height=1).pack(fill='x')

        self.detail_inner = tk.Frame(self.detail_card, bg=COLORS['card_bg'])
        self.detail_inner.pack(fill='both', expand=True, padx=4, pady=4)

        self._show_detail_placeholder()
        self.load_products()

    def load_products(self, search='', category_id=None):
        rows = db.get_products(search=search, category_id=category_id)
        self.table.load([
            (r['id'], r['title'], r['brand'], r['category'] or '—',
             f"${r['price']}", r['quantity_available'],
             r['quantity_sold'], f"${r['total_price_sold']}")
            for r in rows
        ], tag_fn=lambda v: 'success' if int(v[5]) > 0 else 'danger')
        self.count_label.config(text=f' {self.table.row_count()} products ')

    def _on_search(self, text):
        cat_id = self._get_selected_category_id()
        self.load_products(search=text, category_id=cat_id)

    def _on_filter_change(self, event=None):
        search = self.search_entry.get()
        cat_id = self._get_selected_category_id()
        self.load_products(search=search, category_id=cat_id)

    def _get_selected_category_id(self):
        name = self.category_var.get()
        for cid, cname in self.categories:
            if cname == name and cid:
                return cid
        return None

    def _on_row_select(self, values):
        product_id = values[0]
        row = db.get_product_detail(product_id)
        if row:
            self._show_detail(row)

    def _show_detail_placeholder(self):
        for w in self.detail_inner.winfo_children():
            w.destroy()
        tk.Label(
            self.detail_inner,
            text='← Select a product\nto view details',
            font=FONTS['body'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_muted'],
            justify='center',
        ).pack(expand=True)

    def _show_detail(self, row):
        for w in self.detail_inner.winfo_children():
            w.destroy()

        fields = [
            ('ID',          row['id']),
            ('Title',       row['title']),
            ('Brand',       row['brand']),
            ('Category',    row['category_name']),
            ('Topic',       row['topic_name']),
            ('Price',       f"${row['price']}"),
            ('In Stock',    row['quantity_available']),
            ('Sold',        row['quantity_sold']),
            ('Revenue',     f"${row['total_price_sold']}"),
            ('Last Sold',   str(row['last_sold_date'] or '—')[:10]),
            ('Uploaded',    str(row['date_uploaded'] or '—')[:10]),
        ]

        for i, (label, value) in enumerate(fields):
            self.make_label_value(self.detail_inner, label, value, i)

'''
refund views - Refund requests list with status filter and 
item sub-table.

'''

STATUS_COLORS = {
    'PENDING_RETURN':    'warning',
    'PRODUCT_RECEIVED':  'info',
    'PROCESSING_REFUND': 'info',
    'COMPLETED':         'success',
    'REJECTED':          'danger',
    'CANCELLED':         'odd',
}


class RefundsView(BaseView):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.make_header('🔄  Refund Requests', 'All synced refund requests from Gamestore')

        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS['bg'])
        toolbar.pack(fill='x', padx=28, pady=(0, 12))

        search_frame, self.search_entry, _ = self.make_search_bar(
            toolbar, 'Search by customer name or email...', self._on_search, width=32
        )
        search_frame.pack(side='left', padx=(0, 16))

        tk.Label(toolbar, text='Status:', font=FONTS['body'],
                 bg=COLORS['bg'], fg=COLORS['text_secondary']).pack(side='left', padx=(0, 6))

        self.status_var = tk.StringVar(value='All')
        self.status_combo = ttk.Combobox(
            toolbar,
            textvariable=self.status_var,
            values=db.REFUND_STATUSES,
            state='readonly',
            width=22,
            font=FONTS['body'],
        )
        self.status_combo.pack(side='left')
        self.status_combo.bind('<<ComboboxSelected>>', self._on_filter_change)

        self.count_label = tk.Label(
            toolbar, text='',
            font=FONTS['small'],
            bg=COLORS['warning'],
            fg='#ffffff',
            padx=8, pady=3,
        )
        self.count_label.pack(side='right')

        # Paned layout
        paned = tk.PanedWindow(self, orient='vertical', bg=COLORS['bg'],
                               sashrelief='flat', sashwidth=6)
        paned.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        # Refunds table
        refunds_card = self.make_card(paned)
        self.refunds_table = DataTable(
            refunds_card,
            columns=[
                ('id',       '#',        50,  'center'),
                ('customer', 'Customer', 170, 'w'),
                ('email',    'Email',    190, 'w'),
                ('order',    'Order #',  70,  'center'),
                ('status',   'Status',   160, 'w'),
                ('reason',   'Reason',   140, 'w'),
                ('amount',   'Amount',   80,  'e'),
                ('verified', 'Verified', 70,  'center'),
                ('date',     'Date',     110, 'center'),
            ],
            on_select=self._on_refund_select,
        )
        self.refunds_table.pack(fill='both', expand=True, padx=8, pady=8)
        paned.add(refunds_card, minsize=200)

        # Refund items card
        items_card = self.make_card(paned)
        self.items_header = tk.Label(
            items_card,
            text='Refund Items  —  select a request above',
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w',
        )
        self.items_header.pack(anchor='w', padx=16, pady=(12, 6))
        tk.Frame(items_card, bg=COLORS['card_border'], height=1).pack(fill='x')

        self.items_table = DataTable(
            items_card,
            columns=[
                ('id',         '#',           50,  'center'),
                ('product',    'Product',      220, 'w'),
                ('qty',        'Qty',          55,  'center'),
                ('amount',     'Refund Amt',   90,  'e'),
                ('condition',  'Condition OK', 90,  'center'),
                ('restocked',  'Restocked',    80,  'center'),
                ('notes',      'Notes',        200, 'w'),
            ],
        )
        self.items_table.pack(fill='both', expand=True, padx=8, pady=8)
        paned.add(items_card, minsize=150)

        self.load_refunds()

    def load_refunds(self, search='', status='All'):
        rows = db.get_refunds(search=search, status_filter=status)
        self.refunds_table.load(
            [
                (r['id'], r['customer_name'], r['customer_email'],
                 r['order_id'], r['status'], r['reason'],
                 f"${r['refund_amount']}",
                 '✓' if r['admin_verified'] else '✗',
                 str(r['created_at'])[:10])
                for r in rows
            ],
            tag_fn=lambda v: STATUS_COLORS.get(v[4], 'odd')
        )
        self.count_label.config(text=f' {self.refunds_table.row_count()} requests ')

    def _on_search(self, text):
        self.load_refunds(search=text, status=self.status_var.get())

    def _on_filter_change(self, event=None):
        self.load_refunds(status=self.status_var.get())

    def _on_refund_select(self, values):
        refund_id = values[0]
        self.items_header.config(
            text=f'Refund Items  —  Request #{refund_id}  •  {values[1]}  •  Status: {values[4]}',
            fg=COLORS['text_primary'],
        )
        items = db.get_refund_items(refund_id)
        self.items_table.load([
            (r['id'], r['title'] or '—', r['quantity_to_refund'],
             f"${r['refund_amount']}",
             '✓' if r['condition_acceptable'] else '✗',
             '✓' if r['restocked'] else '✗',
             r['condition_notes'] or '—')
            for r in items
        ])

'''
reward views - Reward accounts list with transaction history 
sub-table.

'''

class RewardsView(BaseView):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.make_header('⭐  Reward Accounts', 'All synced reward accounts from Gamestore')

        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS['bg'])
        toolbar.pack(fill='x', padx=28, pady=(0, 12))

        search_frame, self.search_entry, _ = self.make_search_bar(
            toolbar, 'Search by username or email...', self._on_search, width=32
        )
        search_frame.pack(side='left')

        self.count_label = tk.Label(
            toolbar, text='',
            font=FONTS['small'],
            bg=COLORS['warning'],
            fg='#ffffff',
            padx=8, pady=3,
        )
        self.count_label.pack(side='right')

        # Paned layout
        paned = tk.PanedWindow(self, orient='vertical', bg=COLORS['bg'],
                               sashrelief='flat', sashwidth=6)
        paned.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        # Accounts table
        accounts_card = self.make_card(paned)
        self.accounts_table = DataTable(
            accounts_card,
            columns=[
                ('id',        '#',              50,  'center'),
                ('username',  'Username',       160, 'w'),
                ('email',     'Email',          200, 'w'),
                ('points',    'Current Points', 120, 'e'),
                ('lifetime',  'Lifetime Points',130, 'e'),
                ('since',     'Member Since',   120, 'center'),
            ],
            on_select=self._on_account_select,
        )
        self.accounts_table.pack(fill='both', expand=True, padx=8, pady=8)
        paned.add(accounts_card, minsize=200)

        # Transactions table
        tx_card = self.make_card(paned)
        self.tx_header = tk.Label(
            tx_card,
            text='Reward Transactions  —  select an account above',
            font=FONTS['subheading'],
            bg=COLORS['card_bg'],
            fg=COLORS['text_secondary'],
            anchor='w',
        )
        self.tx_header.pack(anchor='w', padx=16, pady=(12, 6))
        tk.Frame(tx_card, bg=COLORS['card_border'], height=1).pack(fill='x')

        self.tx_table = DataTable(
            tx_card,
            columns=[
                ('id',     '#',           50,  'center'),
                ('type',   'Type',        140, 'w'),
                ('points', 'Points',      90,  'e'),
                ('total',  'Order Total', 100, 'e'),
                ('desc',   'Description', 300, 'w'),
                ('date',   'Date',        130, 'center'),
            ],
        )
        self.tx_table.pack(fill='both', expand=True, padx=8, pady=8)
        paned.add(tx_card, minsize=150)

        self.load_accounts()

    def load_accounts(self, search=''):
        rows = db.get_reward_accounts(search=search)
        self.accounts_table.load([
            (r['id'], r['username'], r['email'],
             f"${r['total_points']}", f"${r['lifetime_points']}",
             str(r['created_at'])[:10])
            for r in rows
        ])
        self.count_label.config(text=f' {self.accounts_table.row_count()} accounts ')

    def _on_search(self, text):
        self.load_accounts(search=text)

    def _on_account_select(self, values):
        user_id = values[0]
        self.tx_header.config(
            text=f'Reward Transactions  —  {values[1]}  •  Balance: {values[3]}  •  Lifetime: {values[4]}',
            fg=COLORS['text_primary'],
        )
        txs = db.get_reward_transactions(user_id)
        self.tx_table.load(
            [
                (r['id'], r['transaction_type'], f"${r['points_earned']}",
                 f"${r['order_total']}", r['description'] or '—',
                 str(r['created_at'])[:16])
                for r in txs
            ],
            tag_fn=lambda v: 'success' if float(v[2].replace('$', '')) >= 0 else 'danger'
        )

'''
users view - Users list with search.

'''

class UsersView(BaseView):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.make_header('👥  Users', 'All synced users from Gamestore')

        # Toolbar
        toolbar = tk.Frame(self, bg=COLORS['bg'])
        toolbar.pack(fill='x', padx=28, pady=(0, 12))

        search_frame, self.search_entry, _ = self.make_search_bar(
            toolbar, 'Search by username or email...', self._on_search, width=32
        )
        search_frame.pack(side='left')

        self.count_label = tk.Label(
            toolbar, text='',
            font=FONTS['small'],
            bg=COLORS['info'],
            fg='#ffffff',
            padx=8, pady=3,
        )
        self.count_label.pack(side='right')

        # Table card
        card = self.make_card(self)
        card.pack(fill='both', expand=True, padx=28, pady=(0, 16))

        self.table = DataTable(
            card,
            columns=[
                ('id',       'ID',          50,  'center'),
                ('username', 'Username',    150, 'w'),
                ('email',    'Email',       220, 'w'),
                ('fname',    'First Name',  120, 'w'),
                ('lname',    'Last Name',   120, 'w'),
                ('orders',   'Orders',      65,  'center'),
                ('staff',    'Staff',       55,  'center'),
                ('active',   'Active',      55,  'center'),
                ('joined',   'Joined',      120, 'center'),
            ],
        )
        self.table.pack(fill='both', expand=True, padx=8, pady=8)

        self.load_users()

    def load_users(self, search=''):
        rows = db.get_users(search=search)
        self.table.load(
            [
                (r['id'], r['username'], r['email'],
                 r['first_name'] or '—', r['last_name'] or '—',
                 r['order_count'],
                 '✓' if r['is_staff'] else '—',
                 '✓' if r['is_active'] else '✗',
                 str(r['date_joined'])[:10])
                for r in rows
            ],
            tag_fn=lambda v: 'info' if v[6] == '✓' else 'odd'
        )
        self.count_label.config(text=f' {self.table.row_count()} users ')

    def _on_search(self, text):
        self.load_users(search=text)