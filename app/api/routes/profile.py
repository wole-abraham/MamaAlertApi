from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, field_validator
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from enum import Enum



router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

@router.get("/me")
async def get_profile(request: Request, user=Depends(get_current_user)):
    """
    gets user profile
    """
    supabase = request.app.state.supabase
    supabase = await supabase.table("profiles").select("first_name, last_name, email").eq("id", user).execute() 
    return JSONResponse(status_code=200, content=supabase.data)