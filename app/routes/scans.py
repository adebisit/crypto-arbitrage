from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, Request, HTTPException
from middleware.authMiddleware import authenticate_request
from ..models.scan import Scan, ScanUpdate
from mongodb import db
from datetime import timedelta, datetime


router = APIRouter()


@router.post("/")
async def create_scan(request: Request, scan: Scan) -> Scan:
    user = request.state.user
    scan.user_id = user.id
    scan_db = db.scans.insert_one(scan.dict())
    return scan.copy(update={
        "_id": str(scan_db.inserted_id)
    })


@router.get("/")
async def get_scans(request: Request) -> List[Scan]:
    scans = db.scans.find({'user_id': request.state.user.id})

    return [Scan(**scan) for scan in scans]


@router.get("/{scan_id}")
async def get_scan(request: Request, scan_id: str) -> Scan:
    scan_db = db.scans.find_one({'_id': ObjectId(scan_id)})
    if not scan_db:
        raise HTTPException(status_code=400, detail="Not Found")
    if scan_db["user_id"] != request.state.user.id:
        raise HTTPException(status_code=401, detail="Unathorized")
    return Scan(id=scan_id, **scan_db)


@router.patch("/{scan_id}")
async def pause_scan(request: Request, scan_id: str, scan_update: ScanUpdate):
    query = {'_id': ObjectId(scan_id), 'user_id': request.state.user.id}
    scan_db = db.scans.find_one(query)
    if not scan_db:
        raise HTTPException(status_code=400, detail="Not Found")
    
    print(scan_db)
    print(scan_update.json())
    scan_db = db.scans.update_one(query, {'$set': scan_update.json()})
    print(scan_db)
    return Scan(id=scan_id, **scan_db)