import sqlite3
from contextlib import contextmanager
from config import DB_PATH


@contextmanager
def get_connection():
    #Context manager for SQLite connections.
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    try:
        yield conn
    finally:
        conn.close()


def db_exists():
    """Check if the database file exists."""
    return DB_PATH.exists()


def get_dashboard_stats():
    #Return high-level counts for the dashboard cards.
    with get_connection() as conn:
        cur = conn.cursor()
        stats = {}

        tables = {
            'products':        'store_product',
            'orders':          'payment_order',
            'order_items':     'payment_orderitem',
            'refunds':         'payment_refundrequest',
            'reward_accounts': 'account_rewardaccount',
            'users':           'auth_user',
            'categories':      'store_category',
            'topics':          'store_topic',
        }

        for key, table in tables.items():
            try:
                cur.execute(f'SELECT COUNT(*) FROM {table}')
                stats[key] = cur.fetchone()[0]
            except sqlite3.OperationalError:
                stats[key] = 0

        # Total revenue
        try:
            cur.execute('SELECT SUM(amount_paid) FROM payment_order')
            result = cur.fetchone()[0]
            stats['total_revenue'] = result if result else 0.0
        except sqlite3.OperationalError:
            stats['total_revenue'] = 0.0

        # Total reward points in circulation
        try:
            cur.execute('SELECT SUM(total_points) FROM account_rewardaccount')
            result = cur.fetchone()[0]
            stats['total_reward_points'] = result if result else 0.0
        except sqlite3.OperationalError:
            stats['total_reward_points'] = 0.0

        return stats


def get_recent_orders(limit=10):
    #Return the most recent orders.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT o.id, o.full_name, o.email, o.amount_paid, o.date_ordered,
                       u.username
                FROM payment_order o
                LEFT JOIN auth_user u ON o.user_id = u.id
                ORDER BY o.date_ordered DESC
                LIMIT ?
            ''', (limit,))
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_recent_products(limit=8):
    #Return the most recently uploaded products.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT p.id, p.title, p.brand, p.price,
                       p.quantity_available, c.name as category
                FROM store_product p
                LEFT JOIN store_category c ON p.category_id = c.id
                ORDER BY p.date_uploaded DESC
                LIMIT ?
            ''', (limit,))
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_products(search='', category_id=None):
    #Return all products, with optional search and category filter.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            query = '''
                SELECT p.id, p.title, p.brand, c.name as category,
                       p.price, p.quantity_available, p.quantity_sold,
                       p.total_price_sold, p.payment_successful,
                       p.date_uploaded, p.last_sold_date
                FROM store_product p
                LEFT JOIN store_category c ON p.category_id = c.id
                WHERE 1=1
            '''
            params = []
            if search:
                query += ' AND (p.title LIKE ? OR p.brand LIKE ?)'
                params += [f'%{search}%', f'%{search}%']
            if category_id:
                query += ' AND p.category_id = ?'
                params.append(category_id)
            query += ' ORDER BY p.date_uploaded DESC'
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_product_detail(product_id):
    #Return full detail for a single product.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT p.*, c.name as category_name, t.name as topic_name
                FROM store_product p
                LEFT JOIN store_category c ON p.category_id = c.id
                LEFT JOIN store_topic t ON c.topic_id = t.id
                WHERE p.id = ?
            ''', (product_id,))
            return cur.fetchone()
        except sqlite3.OperationalError:
            return None


def get_categories():
    #Return all categories for filter dropdowns.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('SELECT id, name FROM store_category ORDER BY name')
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_orders(search=''):
    #Return all orders with optional search.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            query = '''
                SELECT o.id, o.full_name, o.email, o.amount_paid,
                       o.date_ordered, u.username,
                       (SELECT COUNT(*) FROM payment_orderitem
                        WHERE order_id = o.id) as item_count
                FROM payment_order o
                LEFT JOIN auth_user u ON o.user_id = u.id
                WHERE 1=1
            '''
            params = []
            if search:
                query += ' AND (o.full_name LIKE ? OR o.email LIKE ?)'
                params += [f'%{search}%', f'%{search}%']
            query += ' ORDER BY o.date_ordered DESC'
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_order_items(order_id):
    #Return all items for a specific order.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT oi.id, p.title, p.brand, oi.quantity, oi.price,
                       (oi.quantity * oi.price) as subtotal
                FROM payment_orderitem oi
                LEFT JOIN store_product p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            ''', (order_id,))
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_order_detail(order_id):
    #Return full detail for a single order.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT o.*, u.username, u.email as user_email
                FROM payment_order o
                LEFT JOIN auth_user u ON o.user_id = u.id
                WHERE o.id = ?
            ''', (order_id,))
            return cur.fetchone()
        except sqlite3.OperationalError:
            return None


def get_refunds(search='', status_filter='All'):
    #Return all refund requests with optional filters.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            query = '''
                SELECT r.id, r.customer_name, r.customer_email,
                       r.order_id, r.status, r.reason,
                       r.refund_amount, r.admin_verified, r.created_at
                FROM payment_refundrequest r
                WHERE 1=1
            '''
            params = []
            if search:
                query += ' AND (r.customer_name LIKE ? OR r.customer_email LIKE ?)'
                params += [f'%{search}%', f'%{search}%']
            if status_filter and status_filter != 'All':
                query += ' AND r.status = ?'
                params.append(status_filter)
            query += ' ORDER BY r.created_at DESC'
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_refund_items(refund_id):
    #Return items for a specific refund request.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT ri.id, p.title, ri.quantity_to_refund,
                       ri.refund_amount, ri.condition_acceptable,
                       ri.restocked, ri.condition_notes
                FROM payment_refunditem ri
                LEFT JOIN payment_orderitem oi ON ri.order_item_id = oi.id
                LEFT JOIN store_product p ON oi.product_id = p.id
                WHERE ri.refund_request_id = ?
            ''', (refund_id,))
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


REFUND_STATUSES = [
    'All',
    'PENDING_RETURN',
    'PRODUCT_RECEIVED',
    'PROCESSING_REFUND',
    'COMPLETED',
    'REJECTED',
    'CANCELLED',
]


def get_reward_accounts(search=''):
    #Return all reward accounts."""
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            query = '''
                SELECT ra.id, u.username, u.email,
                       ra.total_points, ra.lifetime_points, ra.created_at
                FROM account_rewardaccount ra
                LEFT JOIN auth_user u ON ra.user_id = u.id
                WHERE 1=1
            '''
            params = []
            if search:
                query += ' AND (u.username LIKE ? OR u.email LIKE ?)'
                params += [f'%{search}%', f'%{search}%']
            query += ' ORDER BY ra.total_points DESC'
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_reward_transactions(user_id):
    #Return reward transactions for a specific user.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                SELECT rt.id, rt.transaction_type, rt.points_earned,
                       rt.order_total, rt.description, rt.created_at
                FROM account_rewardtransaction rt
                WHERE rt.user_id = ?
                ORDER BY rt.created_at DESC
            ''', (user_id,))
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []


def get_users(search=''):
    #Return all users.
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            query = '''
                SELECT u.id, u.username, u.email, u.first_name, u.last_name,
                       u.is_staff, u.is_active, u.date_joined,
                       (SELECT COUNT(*) FROM payment_order WHERE user_id = u.id) as order_count
                FROM auth_user u
                WHERE 1=1
            '''
            params = []
            if search:
                query += ' AND (u.username LIKE ? OR u.email LIKE ?)'
                params += [f'%{search}%', f'%{search}%']
            query += ' ORDER BY u.date_joined DESC'
            cur.execute(query, params)
            return cur.fetchall()
        except sqlite3.OperationalError:
            return []
        



