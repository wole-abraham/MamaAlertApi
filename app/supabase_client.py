import dotenv
import os
import logging

from supabase import acreate_client, AsyncClient

logger = logging.getLogger(__name__)

dotenv.load_dotenv()
url:str = os.getenv("PROJECT_URL")
key:str = os.getenv("API_KEY")

project_jwt:str = os.getenv("PROJECT_JWT")


async def create_supabase():
    logger.info(f"Creating Supabase client for URL: {url[:20]}...")
    try:
        supabase: AsyncClient = await acreate_client(url, key)
        logger.info("Supabase client created successfully")
        return supabase
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        raise


