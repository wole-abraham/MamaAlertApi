from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from fastapi.responses import Response, JSONResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/baby",
                   tags=["baby_symptoms"])


class babyHealth(BaseModel):
        symptom: str
        baby_id: str
        severity:str
        note: Optional[str]
        date: date
        time:time

@router.post("/symptoms")
async def BabyHealth(request: Request, payload:babyHealth, user=Depends(get_current_user)):
    logger.info(f"Logging baby symptom for user: {user}")
    payload = payload.model_dump()
    payload['user_id'] = user
    payload['date'] = payload["date"].isoformat()
    payload['time'] = payload['time'].isoformat()
    supabase = request.app.state.supabase
    try:
        await supabase.table("baby_health_log").insert(payload).execute()
        logger.info(f"Baby symptom logged successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to log baby symptom for user {user}: {str(e)}")
        raise
    return Response(status_code=200)

@router.get("/")
async def BabyHealth(request: Request,user=Depends(get_current_user)):
    logger.info(f"Fetching baby health logs for user: {user}")
    supabase = request.app.state.supabase
    res = await supabase.table("baby_health_log").select(
        "symptom",
        'severity',
        "note",
        "date",
        "time"
    ).eq("user_id", user).execute()
    logger.info(f"Retrieved {len(res.data)} baby health logs for user: {user}")
    return JSONResponse(status_code=200, content=res.data)

