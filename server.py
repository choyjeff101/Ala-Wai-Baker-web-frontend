import sqlite3
import json
from flask import Flask, request, jsonify, redirect, url_for, render_template, send_from_directory
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8000"]}})

# Serve static files from the root directory
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/order')
def order_page():
    return render_template('order.html')

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

    # Create products table if it doesn't exist
    conn.execute('''
      CREATE TABLE IF NOT EXISTS products (
        ProductID INTEGER PRIMARY KEY,
        ProductName TEXT UNIQUE,
        FullcacciaPrice REAL,
        HalfocacciaPrice REAL
      )
    ''')

    # Insert default products if they don't exist
    conn.execute('''
      INSERT OR IGNORE INTO products (ProductName, FullcacciaPrice, HalfocacciaPrice)
      VALUES 
        ('The Original', 10.00, 6.00),
        ('The Classic', 10.00, 6.00),
        ('The Ala Wai', 10.00, 6.00)
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
    
    # Return JSON response instead of redirecting
    return jsonify({
        'status': 'success',
        'order_id': order_id,
        'confirmation_url': f'/order-confirmation/{order_id}'
    }), 201

# Connect to orders.db
def get_db_connection():
    conn = sqlite3.connect('orders.db')
    conn.row_factory = sqlite3.Row  # to allow dict-like access
    return conn

@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    conn = get_db_connection() # A helper function that returns a connection with row_factory set.
    # Retrieve the order from the orders table.
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order is None:
        conn.close()
        return "Order not found", 404

    # Fetch product prices from the products table
    products = conn.execute('SELECT * FROM products').fetchall()
    product_prices = {}
    for product in products:
        product_prices[product['ProductName']] = {
            'FullcacciaPrice': product['FullcacciaPrice'],
            'HalfocacciaPrice': product['HalfocacciaPrice']
        }

    # Parse the products JSON string into a list of product objects.
    try:
        product_quantities = json.loads(order['products'])
    except Exception as e:
        conn.close()
        return "Error parsing product data", 500

    line_items = []

    # Iterate over each product object in the list.
    for prod in product_quantities:
        # Each 'prod' is a dictionary with keys 'productType', 'fullcacciaQty', and 'halfoccaiaQty'
        prod_name = prod.get('productType')
        qty_full = prod.get('fullcacciaQty', 0)
        qty_half = prod.get('halfoccaiaQty', 0)

        # Look up unit prices for Fullcaccia and Halfoccaia from your products table.
        # Use the product name from the order to look up prices
        product_price_info = product_prices.get(prod_name, {})
        unit_price_full = product_price_info.get('FullcacciaPrice', 0.0)
        unit_price_half = product_price_info.get('HalfocacciaPrice', 0.0)

        # Add line items for each quantity
        if qty_full:
            line_items.append({
                'product_name': prod_name + " Fullcaccia",
                'quantity': qty_full,
                'unit_price': unit_price_full
            })
        if qty_half:
            line_items.append({
                'product_name': prod_name + " Halfoccaia",
                'quantity': qty_half,
                'unit_price': unit_price_half
            })

    # Calculate total as sum of unit prices
    total_order = sum(item['unit_price'] for item in line_items)

    # Pass the order and computed line items to the template.
    return render_template('order_confirmation.html',
                       order=order,
                       line_items=line_items,
                       total_order=total_order)
    
if __name__=='__main__':
    init_db()
    app.run(debug=True)
