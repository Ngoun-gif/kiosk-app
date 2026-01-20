from src.kiosk.data.db import init_db, get_conn

class Api:
    def __init__(self):
        init_db()

    def list_products(self):
        with get_conn() as c:
            rows = c.execute(
                "SELECT id, name, price FROM products WHERE is_active=1 ORDER BY id"
            ).fetchall()
        return [{"id": r[0], "name": r[1], "price": r[2]} for r in rows]
