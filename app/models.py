import sqlite3
import json
import os

def get_db_connection():
    conn = sqlite3.connect('instance/orders.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
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

    # Create products table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            ProductID INTEGER PRIMARY KEY,
            ProductName TEXT UNIQUE,
            FullcacciaPrice REAL,
            HalfocacciaPrice REAL
        )
    ''')

    # Insert default products
    conn.execute('''
        INSERT OR IGNORE INTO products (ProductName, FullcacciaPrice, HalfocacciaPrice)
        VALUES 
            ('The Original', 10.00, 5.00),
            ('The Classic', 10.00, 5.00),
            ('The Ala Wai', 10.00, 5.00)
    ''')

    conn.commit()
    conn.close()

def create_order(data):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO orders (fullName, phone, pickupDate, pickupTime, products)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['fullName'],
        data['phone'],
        data['pickupDate'],
        data['pickupTime'],
        json.dumps(data['products'])
    ))
    
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return order_id 