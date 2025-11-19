import dotenv
import os
import requests
from jose import jwt

import os
import asyncio
from supabase import acreate_client, AsyncClient

dotenv.load_dotenv()
url:str = os.getenv("PROJECT_URL")
key:str = os.getenv("API_KEY")

project_jwt:str = os.getenv("PROJECT_JWT")


async def create_supabase():
    supabase: AsyncClient = await acreate_client(url, key)
    return supabase


