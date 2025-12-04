from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from fastapi.responses import Response



router = APIRouter(
    prefix="/period_log",
    tags=["period_log"]

)

class period_log(BaseModel):
    start: date
    flow_level: str
    symptoms: Optional[List]


@router.post("/")
async def log_period(request: Request, payload:period_log, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    table  = supabase.table("log_period")
    data = payload.model_dump()
    data["user_id"] = user
    data["start"] = data["start"].isoformat()
    print(data, type(data))
    await table.insert(data).execute()
    return Response(status_codje=201)
