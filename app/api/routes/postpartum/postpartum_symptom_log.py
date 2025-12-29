from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user
from pydantic import BaseModel
from typing import Optional
from datetime import date, time
from fastapi.responses import Response, JSONResponse



router = APIRouter(
    prefix="/post-partum-log"
)

class PostPartum(BaseModel):
    symptom: str
    severity_level:str
    notes: Optional[str]
    date: date
    time: time


@router.post("/")
async def symptom_post(request:Request, payload:PostPartum, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    payload = payload.model_dump()
    payload['user_id'] = user
    payload['date'] = payload['date'].isoformat()
    payload['time'] = payload['time'].isoformat()
    await supabase.table("postpartum_symptomo_log").insert(payload).execute()
    return Response(status_code=201)

@router.get("/")
async def symptom_get(request: Request, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    res = await supabase.table("postpartum_symptom_log").select(
        "symptom",
        "severity_level",
        "date",
        "time"
    ).execute()
    return JSONResponse(status_code=200, content=res.data)