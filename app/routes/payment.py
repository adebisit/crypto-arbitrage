from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from ..utils import payment, token
from ..models.user import User
from ..models.payment import Payment, CardAuthorization
from mongodb import db


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
            user_id = user.id,
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
        raise HTTPException(status_code=500, detail="Could not initialize payment")
    


@router.get('/')
async def get_token_balance(request: Request):
    return {}
