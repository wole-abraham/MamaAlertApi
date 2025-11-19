# from fastapi import APIRouter, Depends
# from fastapi.responses import JSONResponse, Response
# from pydantic import BaseModel
# from datetime import date, time
# from app.supabase_client import supabase
# from app.api.dependencies.auth import get_current_user
# from typing import List
# from enum import Enum


# table = supabase.table("emergency_contact")

# router = APIRouter(
#     prefix="/contact",
#     tags=["emergencyContact"]
# )

# class EmergencyContact(BaseModel):
#     name: str
#     relationship: str
#     phone: str
#     email: str | None=None


# @router.post("/")
# def emergency_contact(contact: EmergencyContact, user=Depends(get_current_user)):
#     """add emergency contact"""
#     data = contact.model_dump()
#     data['user_id'] = user
#     table.insert(data).execute()
#     return Response(status_code=201)
    
# @router.get("/")
# def emergency_contact(user=Depends(get_current_user)):
#     """get emergency contacts"""
#     data = table.select("name", "phone", "relationship", "email").eq("user_id", user).execute()
