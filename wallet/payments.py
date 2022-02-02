import requests
import math
import random

def process_payment(name, amount):
    hed = {'Authorization': 'Bearer ' + 'FLWSECK_TEST-5746d0af39f7689a2590de6454555385-X'}
    data = {
        "tx_ref": '' + str(math.floor(1000000 + random.random() * 9000000)),
        "amount": str(amount),
        "currency": "RWF",
        # "redirect_url": "http://localhost:8000/wallet/callback",
        "payment_options": "card",
        "meta": {
            "consumer_id": 23,
            "consumer_mac": "92a3-912ba-1192a"
        },
        "customer": {
            "email": 'fab.wastee@gmail.com',
            "phonenumber": "0783845574",
            "name": name
        },
        "customizations": {
            "title": "Saving Wallet",
            "description": "Adding Money To Saving Wallet",
            "logo": "https://getbootstrap.com/docs/4.0/assets/brand/bootstrap-solid.svg"
        }
    }
    url = 'https://api.flutterwave.com/v3/payments'
    response = requests.post(url, json=data, headers=hed)
    response = response.json()
    print('=============== response==============',response)
    link = response['data']['link']
    return link