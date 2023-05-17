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


@router.get("/", dependencies=[Depends(authenticate_request)])
async def get_me(request: Request):
    user: User = request.state.user
    # task = my_task.delay("Taiwo")
    # print(task)

    # BackgroundTasks.add_task(email.send_email, "", "", [])
    return UserOut(**user.dict())


@router.post("/change-password", dependencies=[Depends(authenticate_request)])
async def change_password(request: Request):
    data = await request.json()
    user: User = request.state.user
    old_password = data.get("old_password")

    if not bcrypt.checkpw(old_password.encode(), user.password.encode()):
        raise HTTPException(detail='Password is wrong', status_code=400)
    
    new_password = data.get("new_password")
    hashed_password = bcrypt.hashpw(new_password.encode('utf8'), bcrypt.gensalt())
    user.password = hashed_password.decode()
    db.users.update_one({"email": user.email}, {"$set": user.dict()})
    return {"message": "Password Change was succesful"}
    

@router.post('/delete', dependencies=[Depends(authenticate_request)])
async def delete_profile(request: Request):
    user: User = request.state.user
    user.archived = True
    db.users.update_one({"email": user.email}, {"$set": user.dict()})
    return {"message": "Account Deleted Succesfully"}

    
