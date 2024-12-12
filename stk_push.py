import requests
import base64
from datetime import datetime
from get_token import get_mpesa_token
from config import Config

def format_phone_number(phone_number):
    """ Ensure the phone number is in the correct format (254XXXXXXXXX). """
    if phone_number.startswith('0'):
        return f"254{phone_number[1:]}"
    elif not phone_number.startswith('254'):
        return f"254{phone_number}"
    return phone_number

def stk_push(amount, phone_number):
    token = get_mpesa_token()
    
    if not token:
        return {'errorMessage': 'Failed to retrieve token'}

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{Config.MPESA_SHORTCODE}{Config.MPESA_PASSKEY}{timestamp}".encode()).decode()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    formatted_phone_number = format_phone_number(phone_number)

    payload = {
        "BusinessShortCode": Config.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": formatted_phone_number,  # Ensure correct phone format
        "PartyB": Config.MPESA_SHORTCODE,
        "PhoneNumber": formatted_phone_number,  # Ensure correct phone format
        "CallBackURL": Config.MPESA_CALLBACK_URL,
        "AccountReference": "Donation",
        "TransactionDesc": "Donation Payment"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # Use sandbox URL for testing

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
    except requests.exceptions.HTTPError as http_err:
        return {"errorMessage": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"errorMessage": f"Other error occurred: {err}"}
    
    # Log the response for debugging
    print("Response Status Code:", response.status_code)
    try:
        response_data = response.json()
        print("Response Body:", response_data)
        return response_data
    except ValueError:
        return {"errorMessage": "Invalid response format"}
