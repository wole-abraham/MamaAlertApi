from  fastapi import HTTPException,  Header
from jose import jwt
import os
import logging

logger = logging.getLogger(__name__)

project_jwt  = os.getenv("PROJECT_JWT")

def verify_token(token: str):
    "returns the user id from token"
    try:
        logger.debug("Attempting to verify JWT token")
        user = jwt.decode(
            token,
            project_jwt,
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id = user.get("sub")
        logger.info(f"Token verified successfully for user: {user_id}")
        return user_id
    except Exception as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid  token")

def get_current_user(authorization: str = Header(None)):
    """Verifies the token from header and returns the payload containing ther user.id"""
    if not authorization:
        logger.warning("Missing Authorization Header in request")
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    token = authorization.replace("Bearer ", "")
    return verify_token(token)
