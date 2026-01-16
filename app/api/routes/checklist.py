from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel
from app.api.dependencies.auth import get_current_user
import logging

logger = logging.getLogger(__name__)


class checkList(BaseModel):
    item_id: int
    checked: bool



router = APIRouter(
    prefix="/checklist",
    tags=['checklist']

)


@router.post("/")
async def upsert(request:Request, list:checkList, user=Depends(get_current_user)):
    logger.info(f"Upserting checklist item for user: {user}")
    supabase = request.app.state.supabase
    list = list.model_dump()
    list["user_id"] = user
    try:
        await supabase.table("bag_checklist").upsert(
            list, on_conflict ="user_id,item_id"
        ).execute()
        logger.info(f"Checklist item upserted successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to upsert checklist for user {user}: {str(e)}")
        raise
    return Response(status_code=201)

