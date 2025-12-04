from fastapi import APIRouter, Depends, Response, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic  import BaseModel, field_validator
from app.api.dependencies.auth import get_current_user
from datetime import time, date
from typing import List


router = APIRouter(
    prefix="/appointment",
    tags=["appointments"]
)

class Appointment(BaseModel):
    appointment_type: str
    appointment_date: date
    appointment_time: time
    hospital_name: str
    doctor: str
    notes: str | None = None

    @field_validator("appointment_date", mode="before")
    def parse_date(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(v)
        except Exception:
            raise ValueError("appointment_date must be YYYY-MM-DD")

    @field_validator("appointment_time", mode="before")
    def parse_time(cls, v):
        if v is None:
            return None
        if isinstance(v, time):
            return v
        try:
            return time.fromisoformat(v)
        except Exception:
            raise ValueError("appointment_time must be HH:MM")


class AppointmentUpdate(Appointment):
    id: str


def _normalize_record_for_db(rec: dict) -> dict:
    r = rec.copy()
    d = r.get("appointment_date")
    if isinstance(d, date):
        r["appointment_date"] = d.isoformat()
    t = r.get("appointment_time")
    if isinstance(t, time):
        r["appointment_time"] = t.isoformat()
    return r


@router.post("/")
async def create_appointment(request: Request, appointment:Appointment, user = Depends(get_current_user)):
    """stores the user appointments"""
    details = appointment.model_dump(exclude=["id"])
    supabase = request.app.state.supabase
    table = supabase.table("appointments")
    details['user_id'] = user
    details = _normalize_record_for_db(details)
    try:
        await table.insert(details).execute()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Input")
    return Response(status_code=204)

@router.post("/bulk")
async def create_bulk_appointments(request: Request, appointments:List[Appointment], user=Depends(get_current_user)):
    """Create appointments in Bulk  """
    supabase = request.app.state.supabase
    table = supabase.table("appointments")
    record = [_normalize_record_for_db(a.model_dump(exclude_none=True)) | {"user_id": user} for a in appointments]
    await table.insert(record).execute()
    return Response(status_code=204)


@router.get("/", response_model=List[Appointment])
async def get_appointments(request: Request,user= Depends(get_current_user)):
    """get the user appointments from db"""
    supabase = request.app.state.supabase
    table = supabase.table("appointments")
    res = await table.select("id",
                       "hospital_name",
                       "appointment_date",
                       "appointment_time",
                       "notes",
                       "doctor",
                       "appointment_type"
                       ).eq("user_id", user).execute()
    return JSONResponse(status_code=200,content=res.data)

@router.patch("/")
async def update_appointment(request: Request, appointment: AppointmentUpdate, user:str=Depends(get_current_user)):
    """ Update appointment info"""
    supabase = request.app.state.supabase
    table = supabase.table("appointments")

    if appointment.id is None:
        raise HTTPException(status_code=400, detail="Missing ID")
    
    record = table.select("*").eq("id", appointment.id).eq("user_id", user).single().execute()
    if not record.data:
        raise HTTPException(status_code=404, detail="Item not found")
    
    details = appointment.model_dump()
    details = _normalize_record_for_db(details)
    await table.update(details).eq("id", appointment.id).execute()
    print(appointment)
    return Response(status_code=204) 