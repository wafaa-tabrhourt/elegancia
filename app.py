from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'elegancia_secret_2024'

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ADMIN_PASSWORD = 'elegancia2024'


def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = sqlite3.connect('database.db')
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, prenom TEXT, adresse TEXT, phone TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER, product_name TEXT, product_price INTEGER,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, price INTEGER, size TEXT, category TEXT, description TEXT
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER, image TEXT,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)
    try:
        db.execute("ALTER TABLE products ADD COLUMN description TEXT")
    except Exception:
        pass
    db.commit()
    db.close()


init_db()


# ── HOME ──
@app.route('/')
def home():
    return render_template('index.html')


# ── WOMEN ──
@app.route('/women')
def women():
    db = get_db()
    rows = db.execute("SELECT * FROM products WHERE category='women'").fetchall()
    products = []
    for p in rows:
        images = db.execute(
            "SELECT image FROM product_images WHERE product_id=?", (p['id'],)
        ).fetchall()
        products.append({
            'id': p['id'], 'name': p['name'], 'price': p['price'],
            'size': p['size'], 'description': p['description'],
            'images': [img['image'] for img in images]
        })
    db.close()
    return render_template('women.html', products=products)


# ── MEN ──
@app.route('/men')
def men():
    db = get_db()
    rows = db.execute("SELECT * FROM products WHERE category='men'").fetchall()
    products = []
    for p in rows:
        images = db.execute(
            "SELECT image FROM product_images WHERE product_id=?", (p['id'],)
        ).fetchall()
        products.append({
            'id': p['id'], 'name': p['name'], 'price': p['price'],
            'size': p['size'], 'description': p['description'],
            'images': [img['image'] for img in images]
        })
    db.close()
    return render_template('men.html', products=products)


# ── ADD TO CART ──
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True
    return redirect('/cart')


# ── CART ──
@app.route('/cart')
def cart():
    db = get_db()
    cart_items = []
    total = 0
    for pid in session.get('cart', []):
        p = db.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if p:
            cart_items.append({'id': p['id'], 'name': p['name'], 'price': p['price']})
            total += p['price']
    db.close()
    return render_template('cart.html', items=cart_items, total=total)


# ── REMOVE FROM CART ──
@app.route('/remove/<int:index>')
def remove(index):
    if 'cart' in session and 0 <= index < len(session['cart']):
        session['cart'].pop(index)
        session.modified = True
    return redirect('/cart')


# ── ORDER ──
@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name    = request.form['name']
        prenom  = request.form['prenom']
        adresse = request.form['adresse']
        phone   = request.form['phone']

        db = get_db()
        cursor = db.execute(
            "INSERT INTO orders (name, prenom, adresse, phone) VALUES (?, ?, ?, ?)",
            (name, prenom, adresse, phone)
        )
        order_id = cursor.lastrowid

        for pid in session.get('cart', []):
            p = db.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            if p:
                db.execute(
                    "INSERT INTO order_items (order_id, product_name, product_price) VALUES (?, ?, ?)",
                    (order_id, p['name'], p['price'])
                )

        db.commit()
        db.close()
        session['cart'] = []
        session.modified = True
        return render_template('success.html', prenom=prenom, name=name)

    db = get_db()
    cart_items = []
    total = 0
    for pid in session.get('cart', []):
        p = db.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if p:
            cart_items.append({'name': p['name'], 'price': p['price']})
            total += p['price']
    db.close()
    return render_template('order.html', items=cart_items, total=total)


# ── ADMIN ──
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin')
        else:
            return render_template('admin.html', logged=False, error='Mot de passe incorrect.')

    if not session.get('admin'):
        return render_template('admin.html', logged=False, error=None)

    db = get_db()

    orders_rows = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    orders = []
    for o in orders_rows:
        items = db.execute(
            "SELECT * FROM order_items WHERE order_id=?", (o['id'],)
        ).fetchall()
        orders.append({
            'id': o['id'], 'name': o['name'], 'prenom': o['prenom'],
            'adresse': o['adresse'], 'phone': o['phone'],
            'produits': [{'name': i['product_name'], 'price': i['product_price']} for i in items],
            'total': sum(i['product_price'] for i in items)
        })

    products_rows = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    products = []
    for p in products_rows:
        images = db.execute(
            "SELECT image FROM product_images WHERE product_id=?", (p['id'],)
        ).fetchall()
        products.append({
            'id': p['id'], 'name': p['name'], 'price': p['price'],
            'size': p['size'], 'category': p['category'],
            'description': p['description'],
            'images': [img['image'] for img in images]
        })

    db.close()
    return render_template('admin.html', logged=True, orders=orders, products=products)


# ── ADD PRODUCT ──
@app.route('/add-product', methods=['POST'])
def add_product():
    if not session.get('admin'):
        return redirect('/admin')

    name        = request.form['name']
    price       = request.form['price']
    size        = request.form['size']
    category    = request.form['category']
    description = request.form.get('description', '')
    images      = request.files.getlist('images')

    db = get_db()
    cursor = db.execute(
        "INSERT INTO products (name, price, size, category, description) VALUES (?, ?, ?, ?, ?)",
        (name, price, size, category, description)
    )
    product_id = cursor.lastrowid

    for image in images:
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.execute(
                "INSERT INTO product_images (product_id, image) VALUES (?, ?)",
                (product_id, filename)
            )

    db.commit()
    db.close()
    return redirect('/admin')


# ── DELETE PRODUCT ──
@app.route('/delete-product/<int:id>')
def delete_product(id):
    if not session.get('admin'):
        return redirect('/admin')
    db = get_db()
    db.execute("DELETE FROM product_images WHERE product_id=?", (id,))
    db.execute("DELETE FROM products WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect('/admin')


# ── DELETE ORDER ──
@app.route('/delete-order/<int:id>')
def delete_order(id):
    if not session.get('admin'):
        return redirect('/admin')
    db = get_db()
    db.execute("DELETE FROM order_items WHERE order_id=?", (id,))
    db.execute("DELETE FROM orders WHERE id=?", (id,))
    db.commit()
    db.close()
    return redirect('/admin')


# ── LOGOUT ──
@app.route('/logout-admin')
def logout_admin():
    session.pop('admin', None)
    return redirect('/admin')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)