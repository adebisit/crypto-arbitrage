import requests
import json
import uuid
from config import settings


def initialize_transaction(email, amount, token_tier, no_tokens):
    resp = requests.post(
        url = "https://api.paystack.co/transaction/initialize",
        headers = {
            "Authorization": "Bearer " + settings.PAYSTACK_SECRET_KEY,
            "Content-Type": "application/json"
        },
        json = {
            "email": email,
            "amount": str(amount),
            "currency": "NGN",
            "channels": ["card", "bank", "bank_transfer"],
            "metadata":{
                "custom_fields":[
                    {
                        "display_name":"Token Tier",
                        "variable_name": "token_tier",
                        "value": token_tier
                    },
                    {
                        "display_name":"Tokens",
                        "variable_name": "no_tokens",
                        "value": no_tokens
                    }
                ]
            }
        }
    )

    data = resp.json()
    if resp.status_code == 200 and data["status"]:
        return data["data"]["authorization_url"], data["data"]["reference"]

    raise Exception("Couldnt initialize payment")    
        


def verify_transaction():
    resp = requests.get(
        url = "https://api.paystack.co/transaction/verify/hi0ucv52kt",
        headers = {
            "Authorization": "Bearer sk_test_4f00025c042f32b86df0ee7c17d62e371f18176e",
            "Content-Type": "application/json"
        }
    )
    print(resp.status_code)
    with open('sandbox/resp2.json', "w+") as fp:
        json.dump(resp.json(), fp, indent=4, sort_keys=True)


def charge_authorization():
    resp = requests.post(
        url = "https://api.paystack.co/transaction/charge_authorization",
        headers = {
            "Authorization": "Bearer sk_test_4f00025c042f32b86df0ee7c17d62e371f18176e",
            "Content-Type": "application/json"
        },
        json = {
            "email": "customer@gmail.com",
            "amount": "20000",
            "authorization_code": "AUTH_7fnkeynlsa"
        }
    )

    print(resp.status_code)
    with open('sandbox/resp3.json', "w+") as fp:
        json.dump(resp.json(), fp, indent=4, sort_keys=True)


# initialize_transaction()
verify_transaction()
# charge_authorization()