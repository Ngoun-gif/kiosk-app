import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("kiosk.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            is_active INTEGER DEFAULT 1
        )
        """)
        # seed once if empty
        count = c.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            c.executemany(
                "INSERT INTO products(name, price) VALUES(?,?)",
                [
                    ("Burger", 3.50),
                    ("Fries",  2.00),
                    ("Coke",   1.50),
                ]
            )
