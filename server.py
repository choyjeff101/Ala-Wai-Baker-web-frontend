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
        pickupDate TEXT,
        pickupTime TEXT,
        products TEXT,
        Received TEXT,
        Progressing TEXT,
        Done TEXT
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
      INSERT INTO orders (fullName, phone, pickupDate, pickupTime, products)
      VALUES (?, ?, ?, ?, ?)
    ''', (
      data['fullName'],
      data['phone'],
      data['pickupDate'],
      data['pickupTime'],
      str(data['products'])
     )
    )

    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'}), 201

if __name__=='__main__':
    init_db()
    app.run(debug=True)
