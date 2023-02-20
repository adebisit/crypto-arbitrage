from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from app.models.user import User, UserIn, UserOut
from mongodb import db
import bcrypt
import uuid
from .. import utils
from datetime import datetime, timedelta
from pytz import timezone
import jwt
from config import settings
from middleware.authMiddleware import authenticate_request
from tasks.tasks import my_task


router = APIRouter()


@router.post('/login')
async def login(username: str, password: str):
    user_db = db.users.find_one({"$or": [{"username": username}, {"email": username}]})
    if user_db is None:
        raise HTTPException(detail='Username or Password is invalid', status_code=401)
    user = UserIn(**user_db)
    if user.is_active == False:
        return {"message": "Please activate your email"}

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(detail='Username or Password is invalid', status_code=401)
    
    encoded_jwt = jwt.encode(dict(UserOut(**user_db)), settings.JWT_SECRET, algorithm="HS256")
    return {"jwt": encoded_jwt}


@router.post('/signup')
async def register(username: str, email: str, password: str):
    user = db.users.find_one({"username": username})
    if user:
        raise HTTPException(detail='Username already exists', status_code=409)
    
    user = db.users.find_one({"email": email})
    if user:
        raise HTTPException(detail='Email is registered', status_code=409)
    
    hashed_password = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    activation_token = str(uuid.uuid4())
    user = User(
        username=username,
        email=email,
        password=hashed_password.decode(),
        activation_token=activation_token
    )
    db.users.insert_one(dict(user)).inserted_id
    # BackgroundTasks.add_task(utils.send_email, "adebisijosephh@gmail.com", activation_token)
    # utils.send_email("adebisijosephh@gmail.com", activation_token)
    
    return {
        "message": f"Registration successful, please check your email for activation instructions @ http://localhost:8000/activate?token={activation_token}"
    }


@router.post('/activate')
async def activate(token: str):
    user_db = db.users.find_one({"activation_token": token})
    if user_db is None:
        raise HTTPException(detail='Invalid Token', status_code=401)
    user = User(**user_db)
    now = datetime.now(timezone("UTC"))
    created_at = timezone("UTC").localize(user.created_at)
    if now - created_at >= timedelta(hours=5):
        raise HTTPException(detail='Expired Token', status_code=401)
    user.is_active = True
    user.activation_token = None
    user.activated_at = now

    db.users.update_one({"_id": user_db["_id"]}, {"$set": user.dict()})
    return {
        "message": "Activation Succesful. You can loggin now."
    }


@router.get("/", dependencies=[Depends(authenticate_request)])
async def get_me(request: Request):
    task = my_task.delay("Taiwo")
    print(task)
    return {"message": "Successful"}