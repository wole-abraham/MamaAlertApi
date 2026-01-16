from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from fastapi.responses import Response, JSONResponse
import logging

logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="/postpartum"
)

class PostPartum(BaseModel):
    symptom: str
    severity_level:str
    notes: Optional[str]
    date: date
    time: time


@router.post("/")
async def symptom_post(request:Request, payload:PostPartum, user=Depends(get_current_user)):
    logger.info(f"Logging postpartum symptom for user: {user}")
    supabase = request.app.state.supabase
    payload = payload.model_dump()
    payload['user_id'] = user
    payload['date'] = payload['date'].isoformat()
    payload['time'] = payload['time'].isoformat()
    try:
        await supabase.table("postpartum_symptomo_log").insert(payload).execute()
        logger.info(f"Postpartum symptom logged successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to log postpartum symptom for user {user}: {str(e)}")
        raise
    return Response(status_code=201)

@router.get("/")
async def symptom_get(request: Request, user=Depends(get_current_user)):
    logger.info(f"Fetching postpartum symptoms for user: {user}")
    supabase = request.app.state.supabase
    res = await supabase.table("postpartum_symptom_log").select(
        "symptom",
        "severity_level",
        "date",
        "time"
    ).execute()
    logger.info(f"Retrieved {len(res.data)} postpartum symptom records for user: {user}")
    return JSONResponse(status_code=200, content=res.data)