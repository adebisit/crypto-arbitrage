from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, Request, HTTPException
from middleware.authMiddleware import authenticate_request
from ..models.scan import Scan
from mongodb import db
from datetime import timedelta


router = APIRouter()


@router.post("/")
async def create_scan(request: Request, scan: Scan) -> Scan:
    user = request.state.user
    db.scans.insert_one({"user_id": user.id, **scan.dict()})
    return Scan(user_id=user.id, **scan.dict())


@router.get("/")
async def get_scans(request: Request) -> List[Scan]:
    print(ObjectId(request.state.user.id))
    scans = db.scans.find({'user_id': request.state.user.id})
    return [Scan(id=str(scan["_id"]), **scan) for scan in scans]


@router.get("/{scan_id}")
async def get_scan(request: Request, scan_id: str) -> Scan:
    scan_db = db.scans.find_one({'_id': ObjectId(scan_id)})
    if not scan_db:
        raise HTTPException(status_code=400, detail="Not Found")
    if scan_db["user_id"] != request.state.user.id:
        raise HTTPException(status_code=401, detail="Unathorized")
    return Scan(id=scan_id, **scan_db)


@router.patch("/{scan_id}")
async def pause_scan(request: Request, scan_id: str):
    pass