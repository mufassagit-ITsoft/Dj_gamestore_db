import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, ROW_HEIGHT

class DataTable(tk.Frame):
    """
    A styled Treeview table wrapped in a Frame with scrollbars.

    Parameters
    ----------
    columns : list of (id, heading, width, anchor) tuples
    on_select : callback(row_values) called when a row is clicked
    """

    def __init__(self, parent, columns, on_select=None, **kwargs):
        super().__init__(parent, bg=COLORS['bg'], **kwargs)
        self.columns = columns
        self.on_select = on_select
        self._sort_reverse = {}
        self._build_style()
        self._build()

    def _build_style(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure(
            'DataTable.Treeview',
            background=COLORS['table_row_odd'],
            foreground=COLORS['text_primary'],
            fieldbackground=COLORS['table_row_odd'],
            font=FONTS['body'],
            rowheight=ROW_HEIGHT,
            borderwidth=0,
        )
        style.configure(
            'DataTable.Treeview.Heading',
            background=COLORS['table_header'],
            foreground='#ffffff',
            font=FONTS['body_bold'],
            borderwidth=0,
            relief='flat',
            padding=(8, 6),
        )
        style.map(
            'DataTable.Treeview',
            background=[('selected', COLORS['table_select'])],
            foreground=[('selected', COLORS['table_select_fg'])],
        )
        style.map(
            'DataTable.Treeview.Heading',
            background=[('active', COLORS['primary'])],
        )

    def _build(self):
        col_ids = [c[0] for c in self.columns]

        # Scrollbars
        v_scroll = ttk.Scrollbar(self, orient='vertical')
        h_scroll = ttk.Scrollbar(self, orient='horizontal')

        # Treeview
        self.tree = ttk.Treeview(
            self,
            columns=col_ids,
            show='headings',
            style='DataTable.Treeview',
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set,
            selectmode='browse',
        )

        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)

        # Configure columns and headings
        for col_id, heading, width, anchor in self.columns:
            self.tree.heading(
                col_id, text=heading,
                command=lambda c=col_id: self._sort_column(c)
            )
            self.tree.column(col_id, width=width, anchor=anchor, minwidth=60)

        # Alternating row colors
        self.tree.tag_configure('odd',  background=COLORS['table_row_odd'])
        self.tree.tag_configure('even', background=COLORS['table_row_even'])
        self.tree.tag_configure('success', background='#f0fff4', foreground='#276749')
        self.tree.tag_configure('danger',  background='#fff5f5', foreground='#c53030')
        self.tree.tag_configure('warning', background='#fffff0', foreground='#975a16')
        self.tree.tag_configure('info',    background='#ebf8ff', foreground='#2c5282')

        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Selection callback
        if self.on_select:
            self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0], 'values')
            self.on_select(values)

    def _sort_column(self, col):
        """Sort rows by column on heading click."""
        rows = [(self.tree.set(item, col), item)
                for item in self.tree.get_children('')]
        reverse = self._sort_reverse.get(col, False)
        try:
            rows.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '')),
                      reverse=reverse)
        except (ValueError, AttributeError):
            rows.sort(key=lambda x: x[0].lower(), reverse=reverse)
        for index, (_, item) in enumerate(rows):
            self.tree.move(item, '', index)
            tag = 'even' if index % 2 == 0 else 'odd'
            self.tree.item(item, tags=(tag,))
        self._sort_reverse[col] = not reverse

    def load(self, rows, tag_fn=None):
        """
        Populate the table with rows.
        rows: list of tuples/sqlite3.Row
        tag_fn: optional callable(row_values) -> tag string
        """
        self.clear()
        for i, row in enumerate(rows):
            values = tuple(row)
            default_tag = 'even' if i % 2 == 0 else 'odd'
            tag = tag_fn(values) if tag_fn else default_tag
            self.tree.insert('', 'end', values=values, tags=(tag,))

    def clear(self):
        """Remove all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def row_count(self):
        return len(self.tree.get_children())
    
