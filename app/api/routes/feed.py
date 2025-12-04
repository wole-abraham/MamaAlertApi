from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from fastapi.exceptions import HTTPException


router = APIRouter(
    prefix="/feed"
)

class Posts(BaseModel):
    title: str
    content: str
    date: date
    time: time

class UserComment(BaseModel):
    content: str
    date: date
    time: time


@router.post("/")
async def create_post(request: Request, payload: Posts, user=Depends(get_current_user)):
    """
        - users creates post
        - 
    """
    supabase  = request.app.state.supabase
    supabase = supabase.table("posts")
    payload = payload.model_dump()
    payload['date'] = payload['date'].isoformat()
    payload['time'] = payload['time'].isoformat()
    payload['profile_id'] = user

    try:
        await supabase.insert(payload).execute()
    except Exception:
        pass
    return Response(status_code=201)


@router.get("/")
async def list_posts(request: Request, user=Depends(get_current_user)):
    """
        list all posts
    """
    supabase = request.app.state.supabase
    supabase = supabase.table("posts")
    res = await supabase.select("id, content, created_at, profiles(first_name, last_name)").execute()
    return JSONResponse(status_code=200, content=res.data)

@router.post("/{post_id}/comment")
async def comment(request:Request, payload: UserComment, post_id: str, user=Depends(get_current_user)):
    """
        post comment from user
    """

    supabase = request.app.state.supabase
    async def check_post(post_id):
        try:
            res = await supabase.table("posts").select("id").eq("id", post_id).execute()
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid Post Id")
        else:
            return True


    if await check_post(post_id):
        supabase = request.app.state.supabase
        supabase = supabase.table("comment")
        payload = payload.model_dump()
        payload['date'] = payload['date'].isoformat()
        payload['time'] = payload['time'].isoformat()
        payload['profile_id'] = user
        payload['post_id'] = post_id
        await supabase.insert(payload).execute()
        return Response(status_code=201)



@router.post("/{post_id}/like")
async def like_Post(request: Request, post_id: str, user=Depends(get_current_user)):
    """Like user posts """
    supabase = request.app.state.supabase
    supabase = supabase.table("post_likes")
    try:
        await supabase.insert({
                "post_id": post_id, "profile_id": user}).execute()
    except Exception:
        return JSONResponse(status_code=200, content={"status": "liked"})

    return JSONResponse(status_code=200, content={"status": "liked"})

@router.delete("/{post_id}/like")
async def unlike_post(request: Request, post_id: str, user=Depends(get_current_user)):
    """UNlike posts"""
    supabase = request.app.state.supabase
    supabase = supabase.table("post_likes")
    try:
        await supabase.delete().eq("post_id", post_id).eq("profile_id", user).execute()
        return JSONResponse(status_code=200, content={"status": "deleted"})
    except Exception:
        return JSONResponse(status_code=200, content={"status": "deleted"})
