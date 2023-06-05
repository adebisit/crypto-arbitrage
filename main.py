from fastapi import FastAPI, HTTPException, Depends
from app.routes import auth, profile, scans, token, webhooks
from middleware import errorMiddleware
from middleware.authMiddleware import authenticate_request 


app = FastAPI()

app.add_exception_handler(HTTPException, errorMiddleware.http_error_handler)
app.add_exception_handler(Exception, errorMiddleware.all_error_handler)

@app.get("/")
async def home():
    return {"message": "Welcome to Crypto Arbitrage API"}
    
app.include_router(auth.router, prefix='/auth')
app.include_router(profile.router, prefix='/profile')
app.include_router(webhooks.router, prefix='/webhooks')
app.include_router(token.router, dependencies=[Depends(authenticate_request)], prefix='/token')
app.include_router(scans.router, dependencies=[Depends(authenticate_request)], prefix="/scans")
# app.route("/auth", users.router)
