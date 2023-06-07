from fastapi import APIRouter, Request, Response, BackgroundTasks
import json
from ..models.payment import CardAuthorization, Payment
from ..models.user import User
from mongodb import db
import hmac
import hashlib
from datetime import datetime
from config import settings
from ..utils import email


router = APIRouter()


@router.post("/payment")
async def process_payment_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    
    hash_value = hmac.new(settings.PAYSTACK_SECRET_KEY.encode('utf-8'), body, hashlib.sha512).hexdigest()
    if hash_value != request.headers["x-paystack-signature"]:
        return Response(status_code=401)

    payload = await request.json()
    data = payload["data"]

    if payload["event"] == "charge.success":
        reference = data["reference"]
        payment_db = db.payments.find_one({"reference_id": reference})
        print("Reference = " + reference)
        print(payment_db)
        payment = Payment(**payment_db)
        payment.status = "completed"
        payment.paid_at = datetime.fromisoformat(data.get("paidAt")[:-1])
        db.payments.update_one({"reference_id": reference}, {"$set": payment.dict()})

        # Get User and update Token
        user_db = db.users.find_one({"username": payment.username})
        user = User(**user_db)
        user.token.available += payment.no_tokens
        db.users.update_one({"email": user.email}, {"$set": user.dict()})

        # Send Email with update
        background_tasks.add_task(
            email.send_email,
            subject=f"{payment.no_tokens} Tokens Added",
            template="token_received.html",
            context={"username": user.username, "no_tokens": payment.no_tokens},
            receiptents=[user.email]
        )

        # Only do this if user wants to save card or if card isnt saved before.
        card_auth = CardAuthorization(
            username = payment.username,
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
    