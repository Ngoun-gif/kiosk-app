from db import init_db, get_conn
import os
from pdf_service import generate_receipt_pdf




class AppApi:
    def __init__(self):
        init_db()

    def ping(self):
        return {"status": "ok", "message": "Python connected"}

    def list_products(self):
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, name, price FROM products WHERE is_active=1 ORDER BY id"
            ).fetchall()
        return [{"id": r[0], "name": r[1], "price": r[2]} for r in rows]

    def get_product(self, product_id: int):
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id, name, price FROM products WHERE id=? AND is_active=1",
                (product_id,),
            ).fetchone()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "price": row[2]}

    def create_order(self, payload: dict):
        """
        payload = {
          "order_type": "DINE_IN" | "TAKE_AWAY",
          "items": [{ "product_id": 1, "qty": 2 }, ...]
        }
        """
        order_type = payload.get("order_type", "DINE_IN")
        items = payload.get("items", [])

        if not items:
            return {"ok": False, "message": "Cart is empty."}

        # Load product data + compute totals
        detailed = []
        total = 0.0
        with get_conn() as conn:
            for it in items:
                pid = int(it.get("product_id"))
                qty = int(it.get("qty", 1))
                if qty <= 0:
                    continue

                row = conn.execute(
                    "SELECT id, name, price FROM products WHERE id=? AND is_active=1",
                    (pid,),
                ).fetchone()
                if not row:
                    return {"ok": False, "message": f"Product not found: {pid}"}

                line_total = float(row[2]) * qty
                total += line_total
                detailed.append({
                    "product_id": row[0],
                    "name": row[1],
                    "price": float(row[2]),
                    "qty": qty,
                    "line_total": line_total
                })

            if not detailed:
                return {"ok": False, "message": "Cart is empty."}

            # Save order
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO orders(order_type, total) VALUES(?, ?)",
                (order_type, total),
            )
            order_id = cur.lastrowid

            # Save items (store snapshot: name/price)
            cur.executemany(
                """INSERT INTO order_items(order_id, product_id, name, price, qty, line_total)
                   VALUES(?,?,?,?,?,?)""",
                [(order_id, d["product_id"], d["name"], d["price"], d["qty"], d["line_total"])
                 for d in detailed],
            )
            conn.commit()

        return {
            "ok": True,
            "order_id": order_id,
            "order_type": order_type,
            "total": total,
            "items": detailed
        }

    
