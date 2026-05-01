import sqlite3

db = sqlite3.connect("database.db")

print("Migration en cours...")

# 1. Ajouter la colonne 'description' si elle n'existe pas
try:
    db.execute("ALTER TABLE products ADD COLUMN description TEXT")
    print("✅ Colonne 'description' ajoutée à products")
except Exception as e:
    print(f"ℹ️  description déjà présente : {e}")

# 2. Créer la table product_images si elle n'existe pas
try:
    db.execute("""
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            image TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)
    print("✅ Table 'product_images' OK")
except Exception as e:
    print(f"ℹ️  product_images : {e}")

# 3. Créer la table order_items si elle n'existe pas
try:
    db.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_name TEXT,
            product_price INTEGER,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    """)
    print("✅ Table 'order_items' OK")
except Exception as e:
    print(f"ℹ️  order_items : {e}")

# 4. S'assurer que orders existe
try:
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            prenom TEXT,
            adresse TEXT,
            phone TEXT
        )
    """)
    print("✅ Table 'orders' OK")
except Exception as e:
    print(f"ℹ️  orders : {e}")

db.commit()
db.close()
print("\n✅ Migration terminée ! Relancez app.py")