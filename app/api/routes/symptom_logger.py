from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, field_validator
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from typing import List
from enum import Enum

router = APIRouter(
    prefix="/logger",
    tags=["logger"]
)


class Severity(str, Enum):
    mild:str = "mild"
    moderate:str = "moderate"
    severe:str = "severe"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val = value.lower()
            for member in cls:
                if member.name.lower() == val or str(member.value).lower() == val:
                    return member
        return None

def _normalize_record_for_db(rec: dict) -> dict:
    r = rec.copy()
    d = r.get("date")
    if isinstance(d, date):
        r["date"] = d.isoformat()
    t = r.get("time")
    if isinstance(t, time):
        r["time"] = t.isoformat()
    return r

class Symptom(BaseModel):
    symptom_type: str
    severity_level: Severity
    date: date
    time:time

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

    @field_validator("time", mode="before")
    def parse_time(cls, v):
        if v is None:
            return None
        if isinstance(v, time):
            return v
        try:
            return time.fromisoformat(v)
        except Exception:
            raise ValueError("time must be HH:MM")

    
@router.post("/")
async def logger(request: Request, logs: Symptom, user:str=Depends(get_current_user)):
    """ symptom logger """
    logs = _normalize_record_for_db(logs.model_dump())
    logs['user_id'] = user
    supabase = request.app.state.supabase
    table = supabase.table("symptom_logs")
    await table.insert(logs).execute()
    return Response(status_code=201)

@router.get("/")
async def logger(request: Request, user=Depends(get_current_user)):
    """ get symptoms log history"""
    supabase = request.app.state.supabase
    table = supabase.table("symptom_logs")
    logs = await table.select(
        "id",
        "symptom_type",
        "date",
        "time"
    ).eq("user_id", user).execute()
    return JSONResponse(status_code=200, content=logs.data)
    