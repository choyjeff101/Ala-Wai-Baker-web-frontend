from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8000"}}, allow_headers=["Content-Type"])

def init_db():
    conn = sqlite3.connect('orders.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS orders (
                      id INTEGER PRIMARY KEY,
                      firstName TEXT, lastName TEXT,
                      phone TEXT, date TEXT, time TEXT,
                      products TEXT)''')
    conn.close()

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    conn = sqlite3.connect('orders.db')
    conn.execute('INSERT INTO orders (firstName, lastName, phone, date, time, products) VALUES (?, ?, ?, ?, ?, ?)',
                 (data['firstName'], data['lastName'], data['phone'],
                  data['pickupDate'], data['pickupTime'], str(data['products'])))
    conn.commit(); conn.close()
    return jsonify({'status':'ok'}), 201

if __name__=='__main__':
    init_db()
    app.run(debug=True)
