from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

products = [
    {"id": 1, "name": "Robe Femme", "price": 200, "size": "M", "category": "women", "image": "women1.jpg"},
    {"id": 2, "name": "T-shirt Homme", "price": 250, "size": "L", "category": "men", "image": "men1.jpg"},
]

def get_db():
    return sqlite3.connect("database.db")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/women")
def women():
    return render_template("women.html", products=[p for p in products if p["category"] == "women"])

@app.route("/men")
def men():
    return render_template("men.html", products=[p for p in products if p["category"] == "men"])

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(product_id)
    session.modified = True
    return redirect("/cart")

@app.route("/cart")
def cart():
    cart_items = []
    total = 0

    for pid in session.get("cart", []):
        for p in products:
            if p["id"] == pid:
                cart_items.append(p)
                total += p["price"]

    return render_template("cart.html", items=cart_items, total=total)

@app.route("/remove/<int:index>")
def remove(index):
    session["cart"].pop(index)
    session.modified = True
    return redirect("/cart")

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        name = request.form["name"]
        prenom = request.form["prenom"]
        adresse = request.form["adresse"]
        phone = request.form["phone"]

        if len(phone) != 10 or not phone.isdigit():
            return "Numéro invalide"

        db = get_db()
        db.execute(
            "INSERT INTO orders (name, prenom, adresse, phone) VALUES (?, ?, ?, ?)",
            (name, prenom, adresse, phone),
        )
        db.commit()

        session["cart"] = []
        return render_template("success.html", name=name, prenom=prenom)

    return render_template("order.html")

@app.route("/admin")
def admin():
    db = get_db()
    orders = db.execute("SELECT * FROM orders").fetchall()
    return render_template("admin.html", orders=orders)

@app.route("/admin-data")
def admin_data():
    db = get_db()
    orders = db.execute("SELECT name, prenom, adresse, phone FROM orders").fetchall()

    result = []
    for o in orders:
        result.append({
            "name": o[0],
            "prenom": o[1],
            "adresse": o[2],
            "phone": o[3]
        })

    return result

if __name__ == "__main__":
    app.run(debug=True)