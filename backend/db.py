import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("kiosk.db")
SCHEMA_PATH = Path(__file__).with_name("schema.sql")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        # seed once
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO products(name, price, is_active) VALUES(?,?,1)",
                [
                    ("Burger", 3.50),
                    ("Fries",  2.00),
                    ("Coke",   1.50),
                    ("Water",  1.00),
                ],
            )
