from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, field_validator
from fastapi.exceptions import HTTPException
from app.api.dependencies.auth import get_current_user
import dotenv
import os
import requests

router = APIRouter(
    prefix="/contact",
    tags=["emergencyContact"]
)

dotenv.load_dotenv()

class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str
    email: str | None=None

    @field_validator("email", mode="before")
    def parse_email(cls, v):
        if v is None:
            return None
        if "@" in v:
            return v
        try:
            if "@" not in v:
              raise ValueError("must a valid email")      
        except Exception:
            raise ValueError("must be a valid email")


@router.post("/")
async def emergency_contact(request: Request, contact: EmergencyContact, user=Depends(get_current_user)):
    """add emergency contact"""
    supabase = request.app.state.supabase
    supabase.table("emergency_contacts")
    data = contact.model_dump()
    data['user_id'] = user
    await supabase.table("emergency_contacts").insert(data).execute()
    return Response(status_code=201)
    
@router.get("/")
async def emergency_contact(request: Request, user=Depends(get_current_user)):
    """get emergency contacts"""
    supabase = request.app.state.supabase
    res = await supabase.table("emergency_contacts").select("name", "phone", "relationship", "email").eq("user_id", user).execute()
    return JSONResponse(status_code=200, content=res.data)

@router.get("/emergency")
async def emergency(request:Request, user=Depends(get_current_user)):
    """Contact emergency contacts
    --refactor nedeed--"""
    supabase = request.app.state.supabase
    res = await supabase.table("emergency_contacts").select("phone").eq("user_id", user).execute()
    user = await supabase.table("profiles").select("first_name", "last_name").eq("id", user).single().execute()
       
    headers={
        "content-type": "application/json"
    }

    payload = {
        "api_key": os.getenv("TERMII_API_KEY"),
        "to": [x['phone'] for x in res.data],
        "from":"MamaAlert",
        "sms": f"{user.data['first_name']} {user.data['last_name']} has an emergency",
        "channel": "generic",
        "type": "plain"
    }
    try:
        requests.post("https://v3.api.termii.com/api/sms/send", json=payload, headers=headers)
    except Exception:
        raise HTTPException(status_code=401)
    return Response(status_code=200)