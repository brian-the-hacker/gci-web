# callback.py

from flask import Blueprint, request, jsonify

callback_bp = Blueprint('callback', __name__)

@callback_bp.route('/mpesa_callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()
    print(f"Received M-Pesa Callback: {data}")
    
    # Handle callback data: log, store, or process the information
    # Example: log the transaction details, update payment status in the database
    
    # Response to Safaricom
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"})
