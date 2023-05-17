from fastapi import Request, APIRouter, BackgroundTasks, HTTPException, Depends, Request
from app.models.user import User, UserIn, UserOut, UserLogIn, UserSignUp
from mongodb import db
import bcrypt
import uuid
from ..utils import email
from datetime import datetime, timedelta
import jwt
from config import settings
from middleware.authMiddleware import authenticate_request
from tasks.tasks import my_task
from config import settings


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
        raise HTTPException(detail='Activation Token is Invalud', status_code=401)
    user = User(**user_db)
    now = datetime.utcnow()

    if is_token_expired(user.token_expires_at):
        raise HTTPException(detail='Activation Token has expired', status_code=401)
    
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
    return {"message": "Activation Succesful. You can log in now."}


@router.post('/login')
async def login(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if username is None:
        raise HTTPException(detail="Missing required parameters: username", status_code=400)
    if password is None:
        raise HTTPException(detail="Missing required parameters: password", status_code=400)

    user_db = db.users.find_one({
        "$and": [
            {"$or": [{"username": username}, {"email": username}]},
            {"archived": False}
        ]
    })
    if user_db is None:
        raise HTTPException(detail='Username or Password is invalid', status_code=401)
    user = UserIn(**user_db)
    if user.is_active == False:
        return {"message": "Please activate your email"}

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(detail='Username or Password is invalid', status_code=401)
    
    encoded_jwt = jwt.encode({
        "exp":datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        **dict(UserOut(**user_db))
    }, settings.JWT_SECRET, algorithm="HS256")
    return {"jwt": encoded_jwt}


@router.post('/password-reset')
async def reset_password(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    user_db = db.users.find_one({"email": data.get("email")})
    if user_db is None:
        raise HTTPException(detail="Account doesnt exist", status_code=404)
    
    token = str(uuid.uuid4())
    user = User(**user_db)
    user.reset_password_token = token
    user.reset_password_token_expires_at = datetime.utcnow() + timedelta(hours=1)
    db.users.update_one({"_id": user_db["_id"]}, {"$set": user.dict()})
    db.users.update_one({"email": user.email}, {"$set": user.dict()})
    
    background_tasks.add_task(
        email.send_email, 
        subject="Reset Password",
        template="reset.html",
        context={"username": user.username, "reset_url": f"{request.base_url}auth/password-reset/{token}"},
        receiptents=[user.email]
    )
    return {"message": f"Password Reset Token Sent: {token}"}


@router.post('/password-reset/{token}')
async def reset_password(request: Request, token: str, background_tasks: BackgroundTasks):
    data = await request.json()
    new_password = data.get("new_password")
    user_db = db.users.find_one({"reset_password_token": token})

    if user_db is None:
        raise HTTPException(detail="Invalid Token", status_code=400)

    user = User(**user_db)
    if is_token_expired(user.reset_password_token_expires_at):
        raise HTTPException(detail='Password Reset Token has expired', status_code=401)

    hashed_password = bcrypt.hashpw(new_password.encode('utf8'), bcrypt.gensalt())
    user.password = hashed_password.decode()
    user.reset_password_token = None
    user.reset_password_token_expires_at = None
    db.users.update_one({"email": user.email}, {"$set": user.dict()})

    background_tasks.add_task(
        email.send_email, 
        subject="Password Reset Succesful",
        template="reset_sucess.html",
        context={"username": user.username},
        receiptents=[user.email]
    )
    return {"message": "Password Reset was succesful"}
