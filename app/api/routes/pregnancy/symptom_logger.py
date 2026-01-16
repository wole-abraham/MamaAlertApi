from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, field_validator
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from enum import Enum
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/symptoms",
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

class SyncSymptoms(BaseModel):
    Symptoms: List[Symptom]


@router.post("/")
async def logger(request: Request, logs: Symptom, user:str=Depends(get_current_user)):
    """ symptom logger """
    logging.getLogger(__name__).info(f"Logging symptom for user: {user}")
    logs = _normalize_record_for_db(logs.model_dump())
    logs['user_id'] = user
    supabase = request.app.state.supabase
    try:
        supabase.table("symptom_logs").insert(logs).execute()
        logging.getLogger(__name__).info(f"Symptom logged successfully for user: {user}")
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to log symptom for user {user}: {str(e)}")
        raise
    return Response(status_code=201)

@router.post("/sync")
async def SyncSymptoms(request: Request, payload: SyncSymptoms, user=Depends(get_current_user)):
    print(payload)
    # await request.app.state.supabase.table("symptom_logs").insert(
    #     payload.model_dump(mode="json")
    # )
@router.get("/")
async def logger(request: Request, user=Depends(get_current_user)):
    """ get symptoms log history"""
    logging.getLogger(__name__).info(f"Fetching symptom logs for user: {user}")
    supabase = request.app.state.supabase
    table = supabase.table("symptom_logs")
    logs = await table.select(
        "id",
        "symptom_type",
        "date",
        "time"
    ).eq("user_id", user).execute()
    logging.getLogger(__name__).info(f"Retrieved {len(logs.data)} symptom logs for user: {user}")
    return JSONResponse(status_code=200, content=logs.data)
    