from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import date, time
from app.api.dependencies.auth import get_current_user
from fastapi.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/feed",
    tags=["feed"]
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


async def check_post(supabase, post_id):
        """
            checks if post exists
        """
        try:
            await supabase.table("posts").select("id").eq("id", post_id).single().execute()
        except Exception:
            raise HTTPException(status_code=404, detail="Post not found")
        else:
            return True

@router.post("/")
async def create_post(request: Request, payload: Posts, user=Depends(get_current_user)):
    """
        - users creates post
        - 
    """
    logger.info(f"Creating post for user: {user}")
    supabase  = request.app.state.supabase
    supabase = supabase.table("posts")
    payload = payload.model_dump()
    payload['date'] = payload['date'].isoformat()
    payload['time'] = payload['time'].isoformat()
    payload['profile_id'] = user

    try:
        await supabase.insert(payload).execute()
        logger.info(f"Post created successfully for user: {user}")
    except Exception as e:
        logger.error(f"Failed to create post for user {user}: {str(e)}")
    return Response(status_code=201)


@router.get("/")
async def list_posts(request: Request, user=Depends(get_current_user)):
    """
        list all posts
    """
    logger.info(f"Fetching posts for user: {user}")
    supabase = request.app.state.supabase
    supabase = supabase.table("posts")
    res = await supabase.select("id, content, created_at, profiles(first_name, last_name)").execute()
    logger.info(f"Retrieved {len(res.data)} posts for user: {user}")
    return JSONResponse(status_code=200, content=res.data)

@router.post("/{post_id}/comment")
async def comment(request:Request, payload: UserComment, post_id: str, user=Depends(get_current_user)):
    """
        post comment from user
    """
    logger.info(f"Adding comment to post {post_id} by user: {user}")
    supabase = request.app.state.supabase   
    
    if await check_post(supabase, post_id):
        supabase = request.app.state.supabase
        supabase = supabase.table("comment")
        payload = payload.model_dump()
        payload['date'] = payload['date'].isoformat()
        payload['time'] = payload['time'].isoformat()
        payload['profile_id'] = user
        payload['post_id'] = post_id
        try:
            await supabase.insert(payload).execute()
            logger.info(f"Comment added to post {post_id} by user: {user}")
        except Exception as e:
            logger.error(f"Failed to add comment for user {user} on post {post_id}: {str(e)}")
            raise
        return Response(status_code=201)


@router.post("/{post_id}/like")
async def like_Post(request: Request, post_id: str, user=Depends(get_current_user)):
    """Like user posts """
    logger.info(f"User {user} liking post: {post_id}")
    supabase = request.app.state.supabase
    supabase = supabase.table("post_likes")
    try:
        await supabase.insert({
                "post_id": post_id, "profile_id": user}).execute()
        logger.info(f"Post {post_id} liked by user: {user}")
    except Exception as e:
        logger.debug(f"Post {post_id} already liked by user {user}: {str(e)}")
        return JSONResponse(status_code=200, content={"status": "liked again"})

    return JSONResponse(status_code=200, content={"status": "liked"})

@router.delete("/{post_id}/like")
async def unlike_post(request: Request, post_id: str, user=Depends(get_current_user)):
    """UNlike posts"""
    logger.info(f"User {user} unliking post: {post_id}")
    supabase = request.app.state.supabase
    await check_post(supabase, post_id)
    supabase = supabase.table("post_likes")
    try:
        await supabase.delete().eq("post_id", post_id).eq("profile_id", user).execute()
        logger.info(f"Post {post_id} unliked by user: {user}")
        return JSONResponse(status_code=200, content={"status": "deleted"})
    except Exception as e:
        logger.error(f"Failed to unlike post {post_id} for user {user}: {str(e)}")
        return JSONResponse(status_code=200, content={"status": "deleted"})


@router.get("/{post_id}/comment")
async def get_comments(request: Request, post_id: str, user=Depends(get_current_user)):
    """
    get comments for -post-id --> post_id
    """
    logger.info(f"Fetching comments for post {post_id} by user: {user}")
    supabase = request.app.state.supabase
    await check_post(supabase, post_id)
    supabase = await supabase.table("comment").select("id, content, date, time, profiles as name (first_name, last_name)").execute()
    logger.info(f"Retrieved {len(supabase.data)} comments for post: {post_id}")
    return JSONResponse(status_code=201, content=supabase.data)

@router.delete("/comment/{comment_id}")
async def delete_comment(request: Request, comment_id: str, user=Depends(get_current_user)):
    """
    Delete comment from user 
    check if user owns the comment
    """
    logger.info(f"Deleting comment {comment_id} by user: {user}")
    supabase = request.app.state.supabase
    try:
        supabase = await supabase.table("comment").select("id").eq("profile_id", user).eq("id", comment_id).single().execute()
        supabase.table("comment").delete().eq("profile_id", user).eq("comment_id", user).execute()
        logger.info(f"Comment {comment_id} deleted successfully by user: {user}")
    except Exception as e:
        logger.warning(f"Comment {comment_id} not found for user {user}: {str(e)}")
        raise HTTPException(status_code=404, detail="post not found")
    else:
        return Response(status_code=200)