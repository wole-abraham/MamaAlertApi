from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/period_log",
    tags=["period_log"]
)

class period_log(BaseModel):
    start: date
    period_staus: str
    flow_level: str
    symptoms: Optional[List]


@router.post("/")
async def log_period(request: Request, payload:period_log, user=Depends(get_current_user)):
    logger.info(f"Logging period for user: {user}")
    supabase = request.app.state.supabase
    table  = supabase.table("log_period")
    data = payload.model_dump()
    data["user_id"] = user
    data["start"] = data["start"].isoformat()
    try:
        await table.insert(data).execute()
        logger.info(f"Period logged successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to log period for user {user}: {str(e)}")
        raise
    return Response(status_code=201)
