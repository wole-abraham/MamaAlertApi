from fastapi import APIRouter, Request, Depends
from app.api.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/babies"
)




@router.post("/growthh")
async def growth_track(request:Request, user=Depends(get_current_user)):
    supabase = request.app.state.supabase
    supabase = supabase.table("baby_tracker")


