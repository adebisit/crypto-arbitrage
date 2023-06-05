from fastapi import APIRouter, Request, Response
import json
from ..models.payment import CardAuthorization, Payment
from mongodb import db
import hmac
import hashlib
from datetime import datetime
from config import settings


router = APIRouter()


def verify_paystack_signature(secret_key, payload, signature):
    computed_signature = hmac.new(secret_key.encode(), payload.encode(), hashlib.sha512).hexdigest()
    return hmac.compare_digest(computed_signature, signature)


@router.post("/payment")
async def process_payment_webhook(request: Request):
    payload = await request.json()
    hash_value = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(), json.dumps(payload).encode(), hashlib.sha512).hexdigest()
    # print(hash_value)
    # print(request.headers["x-paystack-signature"])
    
    # if hash_value != request.headers["x-paystack-signature"]:
    #     return Response(status_code=400)

    data = payload["data"]
    # with open("Test.json", "w+") as fp:
    #     json.dump(data, fp, indent=4, sort_keys=True)

    if payload["event"] == "charge.success":
        reference = data["reference"]
        payment_db = db.payments.find_one({"reference_id": reference})
        print("Reference = " + reference)
        print(payment_db)
        payment = Payment(**payment_db)
        payment.status = "completed"
        payment.paid_at = datetime.fromisoformat(data.get("paidAt")[:-1])
        db.payments.update_one({"reference_id": reference}, {"$set": payment.dict()})

        card_auth = CardAuthorization(
            user_id = payment.user_id,
            authorization_code = data["authorization"]["authorization_code"],
            card_bin = data["authorization"]["bin"],
            brand = data["authorization"]["brand"],
            card_type = data["authorization"]["card_type"],
            last4 = data["authorization"]["last4"],
            exp_month = data["authorization"]["exp_month"],
            exp_year = data["authorization"]["exp_year"]
        )
        db.card_authorizations.insert_one(card_auth.dict())

    return Response(status_code=200)
    