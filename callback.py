<<<<<<< HEAD
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
=======
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
>>>>>>> f8a00e35b77637d46ca2d4b0b6f40c082d27d19c
