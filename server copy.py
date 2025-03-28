from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json

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
        date TEXT,
        time TEXT,
        products TEXT,
        delivery_id INTEGER,
        Received INTEGER,
        Progressing INTEGER,
        Done INTEGER
      )
    ''')

    # Create deliveries table
    # The customer_contact column stores a JSON string combining contact info.   
    conn.execute('''
      CREATE TABLE IF NOT EXISTS deliveries (
        id INTEGER PRIMARY KEY,
        order_id INTEGER UNIQUE NOT NULL,
        customer_contact TEXT
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

# Order insertion route:
    # 1. Insert the order data into the orders table.
    cur.execute('''
      INSERT INTO orders (fullName, phone, date, time, products)
      VALUES (?, ?, ?, ?, ?)
    ''', (
      data['fullName'],
      data['phone'],
      data['pickupDate'],
      data['pickupTime'],
      str(data['products'])
    ))
    order_id = cur.lastrowid

    # 2. Combine customer contact information into a JSON string.
    customer_contact = json.dumps({
        'fullName': data['fullName'],
        'phone': data['phone'],
        'pickupDate': data['pickupDate'],
        'pickupTime': data['pickupTime']
    })

    # 3. Insert a new row into the deliveries table.
    cur.execute('''
      INSERT INTO deliveries (order_id, customer_contact)
      VALUES (?, ?)
    ''', (order_id, customer_contact))
    delivery_id = cur.lastrowid

    # 4. Update the orders table: set delivery_id to the newly created delivery record's id.
    cur.execute('UPDATE orders SET delivery_id = ? WHERE id = ?', (delivery_id, order_id))

    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'order_id': order_id}), 201

if __name__=='__main__':
    init_db()
    app.run(debug=True)
