from fastapi import FastAPI, HTTPException
from app.routes import users
from middleware import errorMiddleware
from middleware.authMiddleware import authenticate_request

app = FastAPI()

app.add_exception_handler(HTTPException, errorMiddleware.http_error_handler)
app.add_exception_handler(Exception, errorMiddleware.all_error_handler)

@app.get("/")
async def home():
    return {"message": "Welcome to Crypto Arbitrage API"}
    
app.include_router(users.router, prefix='/auth')
# app.route("/auth", users.router)
