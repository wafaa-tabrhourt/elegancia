import sqlite3

db = sqlite3.connect("database.db")

db.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    prenom TEXT,
    adresse TEXT,
    phone TEXT
)
""")

db.commit()
db.close()