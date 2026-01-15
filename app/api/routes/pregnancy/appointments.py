from fastapi import APIRouter, Depends, Response, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic  import BaseModel, field_validator
from app.api.dependencies.auth import get_current_user
from datetime import time, date
from typing import List
from supabase import PostgrestAPIError


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


class AppointmentUpdate(BaseModel):
    appointment_type: str | None = None
    appointment_date: date | None = None
    appointment_time: time | None = None
    hospital_name: str | None = None
    doctor: str | None = None
    notes: str | None = None


@router.post("/")
async def create_appointment(request: Request, appointment:Appointment, user = Depends(get_current_user)):
    """stores the user appointments"""
    details = appointment.model_dump(mode="json")
    table = request.app.state.supabase.table("appointments")
    details['user_id'] = user
    try:
        await table.insert(details).execute()
    except PostgrestAPIError:
        raise HTTPException(status_code=400, detail="Invalid request")
    return Response(status_code=204)

@router.get("/", response_model=List[Appointment])
async def get_appointments(request: Request,user= Depends(get_current_user)):
    """get the user appointments from db"""
    supabase = request.app.state.supabase
    table = supabase.table("appointments")
    res = await table.select(
        "id",
        "hospital_name",
        "appointment_date",
        "appointment_time",
        "notes",
        "doctor",
        "appointment_type"
        ).eq("user_id", user).order("appointment_date", desc=False).order("appointment_time", desc=True).execute()
    return JSONResponse(status_code=200,content=res.data)


@router.post("/bulk")
async def create_bulk_appointments(request: Request, appointments:List[Appointment], user=Depends(get_current_user)):
    """Create appointments in Bulk  """
    supabase = request.app.state.supabase
    table = supabase.table("appointments")
    record = [a.model_dump(mode="json") | {"user_id": user} for a in appointments]
    await table.insert(record).execute()
    return Response(status_code=204)


@router.patch("/{appointment_id}")
async def update_appointment(request: Request, appointment_id: str, appointment: AppointmentUpdate, user:str=Depends(get_current_user)):
    """ Update User Apppointment
        -- user_id
        -- apppointment_id
    """
    try:
        await request.app.state.supabse.table("appointments").select("*").eq("id", appointment_id).eq("user_id", user).single().execute()
    except PostgrestAPIError:
        raise HTTPException(status_code=404, detail="Appointment does not exist")
    details = appointment.model_dump(mode="json", exclude_unset=True, exclude_none=True)
    await request.app.state.supabse.table("appointments").update(details).eq("id", id).eq("user_id", user).execute()
    return Response(status_code=204) 

@router.delete("/{appointment_id}")
async def delete_appointment(request: Request,  appointment_id: str, user=Depends(get_current_user)):
    """
        Deletes Appointment
    """
    try:
        await request.app.state.supabase.table("appointments").select("*").eq("id", appointment_id).eq("user_id", user).single().execute()
    except PostgrestAPIError:
        raise HTTPException(status_code=404, detail="Appointment does not exist")
    await request.app.state.supabase.table("appointments").delete().eq("id", appointment_id).eq("user_id", user).execute()
    return Response(status_code=204)