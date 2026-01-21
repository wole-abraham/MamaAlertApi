from fastapi import FastAPI
import logging

from .api.routes.profile import profile

from .api.routes.community import feed

from .api.routes.postpartum import baby_profiles, baby_symptom
from .api.routes import checklist, find_care
from .api.routes.pregnancy import appointments, emergency, symptom_logger, trackers
from .api.routes.menstral import daily_log, log_period
from app.supabase_client import create_supabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



app = FastAPI(
    title="MamaAlertAPI",
    description="API endpoints",
    version="1.0.0"
)

@app.get("/")
async def status():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated")
    app.state.supabase = await create_supabase()
    logger.info("Supabase client initialized successfully")

# @app.on_event("shutdown")
# async def shutdown_event():
#     supabase = getattr(app.state, "supabase", None)
#     if supabase:
#         await supabase.close()


app.include_router(appointments.router)
app.include_router(trackers.router)
app.include_router(checklist.router)
# app.include_router(find_care.router)
app.include_router(symptom_logger.router)
app.include_router(emergency.router)
app.include_router(feed.router)
app.include_router(log_period.router)
app.include_router(baby_profiles.router)
app.include_router(baby_symptom.router)
app.include_router(daily_log.router)
app.include_router(profile.router)

