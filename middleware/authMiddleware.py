from fastapi import Request, HTTPException
import jwt
from config import settings
from mongodb import db
from app.models.user import User
from pprint import pprint
from datetime import datetime



async def authenticate_request(request: Request):
    authroization: str = request.headers.get("Authorization")
    if not authroization:
        raise HTTPException(detail='Authorization Header is missing', status_code=401)
    token = authroization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"], options={"verify_exp": True})
        if ('exp' not in payload) or (datetime.utcnow() > datetime.fromtimestamp(payload['exp'])):
            raise HTTPException(detail="Login Token has expired.", status_code=401)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user_db = db.users.find_one({"email": payload["email"]})
    if not user_db:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = User(**user_db, id=str(user_db["_id"]))
    request.state.user = user
