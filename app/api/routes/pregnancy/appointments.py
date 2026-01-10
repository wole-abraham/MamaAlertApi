from fastapi import APIRouter, Depends, Response, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic  import BaseModel, field_validator
from app.api.dependencies.auth import get_current_user
from datetime import time, date
from typing import List


router = APIRouter(
    prefix="/appointment",
    tags=["appointment"]
)

class Appointment(BaseModel):
    appointment_type: str
    appointment_date: date
    appointment_time: time
    hospital_name: str
    doctor: str
    notes: str | None = None


class AppointmentUpdate(Appointment):
    id: str


@router.post("/")
async def create_appointment(request: Request, appointment:Appointment, user = Depends(get_current_user)):
    """stores the user appointments"""
    details = appointment.model_dump(mode="json")
    table = request.app.state.supabase.table("appointments")
    details['user_id'] = user
    try:
        await table.insert(details).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid request")
    return Response(status_code=204)

@router.post("/bulk")
async def create_bulk_appointments(request: Request, appointments:List[Appointment], user=Depends(get_current_user)):
    """Create appointments in Bulk  """
    supabase = request.app.state.supabase
    table = supabase.table("appointments")
    record = [a.model_dump(exclude_none=True, mode="json") | {"user_id": user} for a in appointments]
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
                       ).eq("user_id", user).order("appointment_date", desc=False,).order("appointment_time").execute()
    return JSONResponse(status_code=200,content=res.data)

@router.patch("/{id}")
async def update_appointment(request: Request, id: str, appointment: AppointmentUpdate, user:str=Depends(get_current_user)):
    """ Update appointment info"""
    supabase = request.app.state.supabase
    table = supabase.table("appointments")

    record = table.select("*").eq("id", id).eq("user_id", user).single().execute()
    if not record.data:
        raise HTTPException(status_code=404, detail="Appointment doesn't exist")
    
    details = appointment.model_dump(mode="json", exclude_unset=True)
    await table.update(details).eq("id", id).execute()
    return Response(status_code=204) 