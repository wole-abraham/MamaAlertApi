from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse, Response
from app.api.dependencies.auth import get_current_user
from supabase import PostgrestAPIError
from fastapi.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)




router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

class Profile(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None

@router.get("/me")
async def get_profile(request: Request, user=Depends(get_current_user)):
    """
    gets user profile
    """
    logger.info(f"Fetching profile for user: {user}")
    supabase = request.app.state.supabase
    try:
        await supabase.table("profiles").select("first_name, last_name, email, phone").eq("id", user).single().execute() 
    except PostgrestAPIError:
        logger.warning(f"Profile not found for user: {user}")
        raise HTTPException(status_code=404, detail="profile does not exist")
    supabase = await supabase.table("profiles").select("first_name, last_name, email, phone").eq("id", user).single().execute()
    logger.info(f"Profile retrieved successfully for user: {user}")
    return JSONResponse(status_code=200, content=supabase.data)

@router.patch("/update")
async def update_profile(request: Request, payload: Profile, user=Depends(get_current_user)):
    """
    updates user profile
    """
    logger.info(f"Updating profile for user: {user}")
    try:
        await request.app.state.supabase.table("profiles").select("*").eq("id", user).single().execute()
    except PostgrestAPIError:
        logger.warning(f"Profile not found for user: {user}")
        raise HTTPException(status_code=404, detail="profile doest not exist")
    await request.app.state.supabase.table("profiles").update(payload.model_dump(mode="json", exclude_none=True)).eq("id", user).execute()
    logger.info(f"Profile updated successfully for user: {user}")
    return Response(status_code=204)


