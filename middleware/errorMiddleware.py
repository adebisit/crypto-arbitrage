from fastapi import HTTPException, Request
from starlette.responses import JSONResponse


def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content={ "message": exc.detail },
        status_code=exc.status_code
    )


def all_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"message": str(exc)},
        status_code=500
    )