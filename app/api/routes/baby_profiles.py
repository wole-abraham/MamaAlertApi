from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user
from pydantic import BaseModel
from datetime import date
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import HTTPException

router = APIRouter(prefix="/babies",
                   tags=["baby_profile"])



class babyprofile(BaseModel):
    name: str
    birth_date:date
    birth_weight:float
    birth_height:float
    gender:str


async def check_baby(supabase, baby_id):
    """
        checks baby id if exists
    """
    supabase = await supabase.table("baby_profiles").select('id').eq("id", baby_id).single().execute()
    if not supabase:
        raise HTTPException(status_code=404, detail="id not found")
    return True

@router.post("/")
async def baby_profile(request:Request, payload:babyprofile, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    table = supabase.table("baby_profiles")
    payload = payload.model_dump()
    payload['birth_date'] = payload['birth_date'].isoformat()
    payload['user_id'] = user
    try:
        await table.insert(payload).execute()
    except Exception:
        raise HTTPException(status_code=400)
    return Response(status_code=201)

@router.get("/")
async def babies(request:Request, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    table = supabase.table("baby_profiles")
    res = await table.select(
        "id",
        "name",
        "birth_date",
        "birth_weight",
        "birth_height",
        "gender"
    ).eq("user_id", user).execute()
    return JSONResponse(status_code=200, content=res.data)


@router.get("/{id}")
async def babies(request:Request, id: str,  user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    await check_baby(supabase, id)
    table = supabase.table("baby_profiles")
    res = await table.select(
        "id",
        "name",
        "birth_date",
        "birth_weight",
        "birth_height",
        "gender"
    ).eq("id", id).eq("user_id", user).single().execute()
    return JSONResponse(status_code=200, content=res.data)

@router.patch("/{id}")
async def update_baby(request:Request, id:str, payload: babyprofile,user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    table = supabase.table("baby_profiles")
    payload = payload.model_dump()
    payload['birth_date'] = payload['birth_date'].isoformat()
    try:
        await table.update(payload).eq("user_id", user).eq("id", id).execute()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400)
    return Response(status_code=204)