from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, field_validator
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from typing import List
import logging

logger = logging.getLogger(__name__)




router = APIRouter(
    prefix="/tracker",
    tags = ["weighttracker"]
)


class weightTracker(BaseModel):
    weight: float
    date: date

    @field_validator("date", mode="before")
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(v)
        except Exception:
            raise ValueError("date must be YYYY-MM-DD")

class MovementTracker(BaseModel):
    interval: int
    date: date

    @field_validator("date", mode="before")
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(v)
        except Exception:
            raise ValueError("date must be YYYY-MM-DD")

def _normalize_record_for_db(rec: dict) -> dict:
    r = rec.copy()
    d = r.get("date")
    if isinstance(d, date):
        r["date"] = d.isoformat()
    t = r.get("time")
    if isinstance(t, time):
        r["time"] = t.isoformat()
    return r

@router.post("/weight")
async def weight(request: Request, weight: weightTracker, user=Depends(get_current_user)):
    """ store users weight to db """
    logger.info(f"Recording weight for user: {user}")
    data = _normalize_record_for_db(weight.model_dump())
    data['user_id'] = user
    supabase = request.app.state.supabase
    try:
        await supabase.table("weight_tracker").insert(data).execute()
        logger.info(f"Weight recorded successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to record weight for user {user}: {str(e)}")
        raise
    return Response(status_code=201)

@router.get("/weight", response_model=List[weightTracker])
async def weight(request: Request, user=Depends(get_current_user)):
    """ get weight histories from """
    logger.info(f"Fetching weight history for user: {user}")
    supabase = request.app.state.supabase
    res = await supabase.table("weight_tracker").select("weight", "date").eq("user_id", user).execute()
    logger.info(f"Retrieved {len(res.data)} weight records for user: {user}")
    return JSONResponse(status_code=200, content=res.data)

@router.post("/movement")
async def movement(request:Request, movement: MovementTracker, user=Depends(get_current_user)):
    """ store baby movement intervals to db """
    logger.info(f"Recording baby movement for user: {user}")
    supabase = request.app.state.supabase
    data = _normalize_record_for_db(movement.model_dump())
    data['user_id'] = user
    try:
        await supabase.table("movement_tracker").insert(
            data
        ).execute()
        logger.info(f"Baby movement recorded successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to record baby movement for user {user}: {str(e)}")
        raise
    return Response(status_code=200)

@router.get("/movement", response_model=List[MovementTracker])
async def movement(request: Request,  user=Depends(get_current_user)):
    """ get movement times from db """
    logger.info(f"Fetching baby movement history for user: {user}")
    supabase = request.app.state.supabase
    res = await supabase.table("movement_tracker").select("date", "interval").eq("user_id", user).execute()
    logger.info(f"Retrieved {len(res.data)} movement records for user: {user}")
    return JSONResponse(status_code=200, content=res.data)