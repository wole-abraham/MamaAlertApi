from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from typing import List




router = APIRouter(
    prefix="/tracker",
    tags = ["weighttracker"]
)


class weightTracker(BaseModel):
    weight: float
    date: date

class MovementTracker(BaseModel):
    time: time
    date: date



@router.post("/weight")
async def weight(request: Request, weight: weightTracker, user=Depends(get_current_user)):
    """ store users weight to db """
    data = weight.model_dump()
    data['user_id'] = user
    supabase = request.app.state.supabase
    await supabase.table("weight_tracker").insert(data).execute()
  
    return Response(status_code=201)


@router.get("/weight", response_model=List[weightTracker])
async def weight(request: Request, weight: weightTracker):
    """ get weight histories from """
    supabase = request.app.state.supabase
    res = await supabase.table("weight_table").select("weight", "date").execute()
    return JSONResponse(status_code=200, content=res.data)

@router.post("/movement")
def movement(movement: MovementTracker):
    """ store movement time to db """
    pass
@router.get("/movement")
def movement(movement: MovementTracker):
    """ get movement times from db """
    pass