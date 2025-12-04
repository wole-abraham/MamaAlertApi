from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from app.api.dependencies.auth import get_current_user


class checkList(BaseModel):
    item_id: int
    checked: bool


router = APIRouter(
    prefix="/vaccination"
)

@router.post("/")
async def upsert(request:Request, list:checkList, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    list = list.model_dump()
    list["user_id"] = user
    await supabase.table("vaccination_checklist").upsert(
        list, on_conflict ="user_id,item_id"
    ).execute()
    return Response(status_code=201)

@router.get("/")
async def get_checklist(request: Request,user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    res = supabase.table("vaccination_checklist").select(
        "item",
        "date",
        "checked"
    ).eq("user_id", user).execute()
    return JSONResponse(status_code=200, content=res.data)
