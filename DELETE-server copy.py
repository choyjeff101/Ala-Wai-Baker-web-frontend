import sqlite3
import json
from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Initialize the database
def init_db():
    conn = sqlite3.connect('orders.db')
    conn.execute('PRAGMA foreign_keys = ON;')
    # Create orders table
    conn.execute('''
      CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        fullName TEXT,
        phone TEXT,
        pickupDate TEXT,
        pickupTime TEXT,
        products TEXT,
        Received TEXT,
        Baking TEXT,
        Ready TEXT,
        Paid TEXT
      )
    ''')

    conn.commit()
    conn.close()

# Create a new order
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    conn = sqlite3.connect('orders.db')
    conn.execute('PRAGMA foreign_keys = ON;')
    cur = conn.cursor()

# Insert the order data into the orders table.
    cur.execute('''
      INSERT INTO orders (fullName, phone, pickupDate, pickupTime, products)
      VALUES (?, ?, ?, ?, ?)
    ''', (
      data['fullName'],
      data['phone'],
      data['pickupDate'],
      data['pickupTime'],
      json.dumps(data['products'])  # <-- Use json.dumps here!
     )
    )
    order_id = cur.lastrowid  # Capture the new order id
    conn.commit()
    conn.close()
    # Redirect to the order confirmation page with the order id.
    return redirect(url_for('order_confirmation', order_id=order_id))

# Connect to orders.db
def get_db_connection():
    conn = sqlite3.connect('orders.db')
    conn.row_factory = sqlite3.Row  # to allow dict-like access
    return conn

@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    conn = get_db_connection() # A helper function that returns a connection with row_factory set.
    # 1. Retrieve the order from the orders table.
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order is None:
        conn.close()
        return "Order not found", 404

    # 2. Parse the products JSON from the order.
    try:
        product_quantities = json.loads(order['products'])
    except Exception as e:
        conn.close()
        return "Error parsing product data", 500

line_items = []
total_order = 0.0

    # 3. Retrieve pricing data from the products table.
    products_data = conn.execute('SELECT * FROM products').fetchall()
    conn.close()

    # Create a dictionary for easy lookup by product name.
    product_prices = {}
    for prod in products_data:
        product_prices[prod['ProductName']] = {
            'FullcacciaPrice': prod['FullcacciaPrice'],
            'HalfocacciaPrice': prod['HalfocacciaPrice']
        }

    # 4. Build line items.
    line_items = []
    total_order = 0.0
    for prod_name, quantity in product_quantities.items():
        # For simplicity, assume the product name keys match exactly one of:
        # "Fullcaccia" or "Halfocaccia".
        # Determine the unit price based on the product name.
        if prod_name.lower() == 'fullcaccia':
            unit_price = product_prices.get('Fullcaccia', {}).get('FullcacciaPrice', 0.0)
        elif prod_name.lower() == 'halfocaccia' or prod_name.lower() == 'halfoccaia':
            unit_price = product_prices.get('Halfoccaia', {}).get('HalfocacciaPrice', 0.0)
        else:
            unit_price = 0.0
        line_total = unit_price * quantity
        total_order += line_total
        line_items.append({
            'product_name': prod_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'line_total': line_total
        })

    # Pass the order and computed line items to the template.
    return render_template('order_confirmation.html',
                           order=order,
                           line_items=line_items,
                           total_order=total_order)
    
if __name__=='__main__':
    init_db()
    app.run(debug=True)
