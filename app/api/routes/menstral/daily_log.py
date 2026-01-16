from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from fastapi.responses import Response, JSONResponse
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/menstral-mode",
    tags=["menstra-mode"]
)


class daily_log(BaseModel):
    feeling: str
    symptoms: Optional[List]
    sexual_activity: str
    sleep_quality: int
    stress_level: int
    date: date


@router.post("/daily-log")
async def daily(request: Request, payload: daily_log, user=Depends(get_current_user)):
    """ Post Daily log endpoint """
    logger.info(f"Creating daily log for user: {user}")
    supabase = request.app.state.supabase
    table = supabase.table("daily_log")
    payload = payload.model_dump()
    payload['user_id'] = user
    payload['date'] = payload['date'].isoformat()
    try:
        data = await table.insert(payload).execute()
        logger.info(f"Daily log created successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to create daily log for user {user}: {str(e)}")
        raise
    return Response(status_code=201)

@router.get("/daily-log")
async def daily_logs(request: Request, user=Depends(get_current_user)):
    """ Daily logs for user """
    logger.info(f"Fetching daily logs for user: {user}")
    supabase = request.app.state.supabase
    table = supabase.table("daily_log")
    res = await table.select("feeling",
                             "symptoms",
                             "sexual_activity",
                             "sleep_quality",
                             "stress_level",
                             "date").eq("user_id", user).execute()
    logger.info(f"Retrieved {len(res.data)} daily logs for user: {user}")
    return JSONResponse(status_code=200, content=res.data)
