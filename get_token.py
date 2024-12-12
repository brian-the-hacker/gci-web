# get_token.py

import requests
from requests.auth import HTTPBasicAuth
from config import Config

def get_mpesa_token():
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.get(url, auth=HTTPBasicAuth(Config.MPESA_CONSUMER_KEY, Config.MPESA_CONSUMER_SECRET))
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None
