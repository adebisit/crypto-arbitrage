from typing import List, Union
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from ..utils import payment, token
from ..models.user import User
from ..models.payment import Payment, PaymentOut
from mongodb import db
from datetime import datetime


router = APIRouter()


@router.post('/')
async def add_token(request: Request):
    user: User = request.state.user
    data = await request.json()
    amount = data.get("amount")
    tier = token.TokenTier.from_amount(amount)
    pricing = token.TokenPricing.get_price(tier)
    
    try:
        auth_url, reference = payment.initialize_transaction(
            email=user.email,
            amount=pricing * amount * 100,
            token_tier= str(tier),
            no_tokens= amount
        )
        
        intialized_payment = Payment(
            username = user.username,
            token_tier = str(tier),
            token_pricing = pricing,
            no_tokens = amount,
            amount = pricing * amount,
            reference_id = reference
        )
        db.payments.insert_one(intialized_payment.dict())
        response = JSONResponse(status_code=201, content={"auth_url": auth_url})
        response.headers["Location"] = auth_url
        return response
    except Exception as e:
        print(type(e), str(e))
        raise HTTPException(status_code=500, detail="Payment URL failed to Initialize")
    


@router.get('/')
async def get_token_balance(request: Request):
    user: User = request.state.user    
    return {
        "token": user.token
    }


@router.patch('/lock')
async def lock_token(request: Request):
    data = await request.json()
    lock_amount = data.get("lock_amount")
    if lock_amount is None:
        raise HTTPException(status_code=400, detail="Missing request body: 'lock_amount'")
    user: User = request.state.user

    if user.token.available < lock_amount:
        raise HTTPException(status_code=402, detail="Insufficient Balance.")

    user.token.available -= lock_amount
    user.token.locked += lock_amount
    db.users.update_one({"email": user.email}, {"$set": user.dict()})
    return {"message": f"{lock_amount} conarbs locked."}


@router.get('/history')
async def get_history(
    request: Request,
    start: datetime= None,
    end: datetime = None,
    tier: str = None,
    status: str = None,
    skip: int = Query(0, ge=0, description="No of records to skip"),
    limit: int = Query(0, ge=0, lt=51, description="No of records to retrieve")
) -> List[PaymentOut]:
    user: User = request.state.user
    queries = [{"username": user.username}]

    if start:
        queries.append({"timestamp": {"$gt": start}})
    if end:
        queries.append({"timestamp": {"$lt": end}})
    if tier:
        queries.append({"token_tier": tier.upper()})
    if status:
        queries.append({"status": status.lower()})
    
    query = {"$and": queries}
    payments_db = db.payments.find(query).skip(skip).limit(limit)
    return list(payments_db)
