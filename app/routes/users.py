from fastapi import Request, APIRouter, BackgroundTasks, HTTPException, Depends, Request
from app.models.user import User, UserIn, UserOut, UserLogIn, UserSignUp
from mongodb import db
import bcrypt
import uuid
from ..utils import email
from datetime import datetime, timedelta
from pytz import timezone
import jwt
from config import settings
from middleware.authMiddleware import authenticate_request
from tasks.tasks import my_task



router = APIRouter()


@router.post('/signup')
async def register(request: Request, userData: UserSignUp, background_tasks: BackgroundTasks):
    user = db.users.find_one({"username": userData.username})
    if user:
        raise HTTPException(detail='Username already exists', status_code=409)
    
    user = db.users.find_one({"email": userData.email})
    if user:
        raise HTTPException(detail='Email is registered', status_code=409)
    
    hashed_password = bcrypt.hashpw(userData.password.encode('utf8'), bcrypt.gensalt())
    activation_token = str(uuid.uuid4())
    user = User(
        username=userData.username,
        email=userData.email,
        password=hashed_password.decode(),
        activation_token=activation_token
    )
    db.users.insert_one(dict(user)).inserted_id
    background_tasks.add_task(
        email.send_email, 
        subject="Confirm your Conarbs Account",
        template="verification.html",
        context={"username": userData.username, "activation_url": f"{request.base_url}auth/activate{activation_token}"},
        receiptents=[userData.email]
    )
    
    return {
        "message": f"Registration successful, please check your email for activation instructions @ http://localhost:8000/activate?token={activation_token}"
    }


def is_token_expired(token_expiration: datetime):
    return datetime.utcnow() > token_expiration

@router.post('/activate')
async def activate(request: Request, background_tasks: BackgroundTasks):
    requestData = await request.json()
    token = requestData.get("token")

    user_db = db.users.find_one({"activation_token": token})
    if user_db is None:
        raise HTTPException(detail='Token is Invalud', status_code=401)
    user = User(**user_db)
    now = datetime.utcnow()
    # created_at = timezone("UTC").localize(user.created_at)

    if is_token_expired(user.token_expires_at):
        raise HTTPException(detail='Token has expired', status_code=401)
    
    user.is_active = True
    user.activation_token = None
    user.activated_at = now

    db.users.update_one({"_id": user_db["_id"]}, {"$set": user.dict()})
    background_tasks.add_task(
        email.send_email, 
        subject="Welcome to Conarbs",
        template="welcome.html",
        context={"username": "Josh"},
        receiptents=["adebisijosephh@gmail.com"]
    )
    return {
        "message": "Activation Succesful. You can log in now."
    }


@router.post('/login')
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if username is None:
        raise HTTPException(detail="Missing required parameters: username", status_code=400)
    if password is None:
        raise HTTPException(detail="Missing required parameters: password", status_code=400)

    print(username)
    print(password)
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



@router.get("/", dependencies=[Depends(authenticate_request)])
async def get_me(request: Request, background_tasks: BackgroundTasks):
    # task = my_task.delay("Taiwo")
    # print(task)
    # BackgroundTasks.add_task(email.send_email, "", "", [])
    return {"message": "Successful"}