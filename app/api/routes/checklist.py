from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, field_validator
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from typing import List 


class checkList(BaseModel):
    item_id: int
    checked: bool



router = APIRouter(
    prefix="/checklist"
)


@router.post("/")
async def upsert(request:Request, list:checkList, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    list = list.model_dump()
    list["user_id"] = user
    await supabase.table("bag_checklist").upsert(
        list, on_conflict ="user_id,item_id"
    ).execute()
    return Response(status_code=201)

