from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, field_validator
from fastapi.exceptions import HTTPException

from supabase import PostgrestAPIError
from app.api.dependencies.auth import get_current_user
import dotenv
import os
import requests
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/emergency",
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


@router.post("/add-contact")
async def emergency_contact(request: Request, contact: EmergencyContact, user=Depends(get_current_user)):
    """add emergency contact"""
    logger.info(f"Adding emergency contact for user: {user}")
    supabase = request.app.state.supabase.table("emergency_contacts")
    data = contact.model_dump(mode="json")
    data['user_id'] = user
    try:
        await supabase.table("emergency_contacts").insert(data).execute()
        logger.info(f"Emergency contact added successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to add emergency contact for user {user}: {str(e)}")
        raise
    return Response(status_code=201)
    
@router.get("/contacts")
async def emergency_contact(request: Request, user=Depends(get_current_user)):
    """get emergency contacts"""
    logger.info(f"Fetching emergency contacts for user: {user}")
    supabase = request.app.state.supabase
    res = await supabase.table("emergency_contacts").select("id", "name", "phone", "relationship", "email").eq("user_id", user).execute()
    logger.info(f"Retrieved {len(res.data)} emergency contacts for user: {user}")
    return JSONResponse(status_code=200, content=res.data)

@router.get("/trigger")
async def emergency(request:Request, user=Depends(get_current_user)):
    """Contact emergency contacts
    --refactor nedeed--"""
    logger.warning(f"Emergency triggered for user: {user}")
    supabase = request.app.state.supabase
    res = await supabase.table("emergency_contacts").select("phone").eq("user_id", user).execute()
    user_data = await supabase.table("profiles").select("first_name", "last_name").eq("id", user).single().execute()
       
    headers={
        "content-type": "application/json"
    }

    payload = {
        "api_key": os.getenv("TERMII_API_KEY"),
        "to": [x['phone'] for x in res.data],
        "from":"MamaAlert",
        "sms": f"{user_data.data['first_name']} {user_data.data['last_name']} has an emergency",
        "channel": "generic",
        "type": "plain"
    }
    try:
        response = requests.post("https://v3.api.termii.com/api/sms/send", json=payload, headers=headers)
        logger.info(f"Emergency SMS sent to {len(res.data)} contacts for user: {user}")
    except Exception as e:
        logger.error(f"Failed to send emergency SMS for user {user}: {str(e)}")
        raise HTTPException(status_code=401)
    return Response(status_code=200)
    
@router.delete("/delete-contact/{id}")
async def delete_contact(request: Request, id:str, user=Depends(get_current_user)):
    logger.info(f"Deleting emergency contact {id} for user: {user}")
    supabase = request.app.state.supabase
    try:
        await supabase.table("emergency_contacts").select("*").eq("id", id, "user_id", user).single().execute()
    except PostgrestAPIError:
        logger.warning(f"Emergency contact {id} not found for user: {user}")
        raise HTTPException(status_code=404, detail="contact does not exist")
    else:
        await supabase.table("emergency_contacts").delete().eq("id", id, "user_id", user).execute()
        logger.info(f"Emergency contact {id} deleted successfully for user: {user}")
        return Response(status_code=204)
    