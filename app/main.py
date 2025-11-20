from fastapi import FastAPI
from .api.routes import appointments, trackers, find_care, symptom_logger, emergency, checklist
from app.supabase_client import create_supabase

app = FastAPI(
    title="MamaAlertAPI",
    description="API endpoints",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    app.state.supabase = await create_supabase()

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
# app.include_router(emergency.router)