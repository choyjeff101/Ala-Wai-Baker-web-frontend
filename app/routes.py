from flask import Blueprint, render_template, request, jsonify
from app.models import get_db_connection, create_order
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/order')
def order_page():
    return render_template('order.html')

@main.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"status": "success", "message": "API is working"}), 200

@main.route('/api/orders', methods=['POST'])
def handle_order():
    data = request.get_json()
    order_id = create_order(data)
    return jsonify({
        'status': 'success',
        'order_id': order_id,
        'confirmation_url': f'/order-confirmation/{order_id}'
    }), 201

@main.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order is None:
        conn.close()
        return "Order not found", 404

    # Fetch product prices
    products = conn.execute('SELECT * FROM products').fetchall()
    product_prices = {
        product['ProductName']: {
            'FullcacciaPrice': product['FullcacciaPrice'],
            'HalfocacciaPrice': product['HalfocacciaPrice']
        } for product in products
    }

    # Process order items
    line_items = []
    for prod in json.loads(order['products']):
        prod_name = prod['productType']
        qty_full = prod.get('fullcacciaQty', 0)
        qty_half = prod.get('halfoccaiaQty', 0)

        product_price_info = product_prices.get(prod_name, {})
        unit_price_full = product_price_info.get('FullcacciaPrice', 0.0)
        unit_price_half = product_price_info.get('HalfocacciaPrice', 0.0)

        if qty_full:
            line_items.append({
                'product_name': f"{prod_name} Fullcaccia",
                'quantity': qty_full,
                'unit_price': unit_price_full
            })
        if qty_half:
            line_items.append({
                'product_name': f"{prod_name} Halfoccaia",
                'quantity': qty_half,
                'unit_price': unit_price_half
            })

    total_order = sum(item['unit_price'] for item in line_items)
    conn.close()

    return render_template('order_confirmation.html',
                         order=order,
                         line_items=line_items,
                         total_order=total_order) 