from  fastapi import HTTPException,  Header
from jose import jwt
import os

project_jwt  = os.getenv("PROJECT_JWT")

def verify_token(token: str):
    "returns the user id from token"
    try:
        user = jwt.decode(
            token,
            project_jwt,
            algorithms=["HS256"],
            audience="authenticated"
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid  token")
    return user.get("sub")

def get_current_user(authorization: str = Header(None)):
    """Verifies the token from header and returns the payload containing ther user.id"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    token = authorization.replace("Bearer ", "")
    return verify_token(token)
