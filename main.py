# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import loads, schedule, events

app = FastAPI(
    title="Load Scheduler API",
    description="Automated Home Electrical Load Scheduler — REST API",
    version="1.0.0",
)

# Allow Next.js frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(loads.router, prefix="/api")
app.include_router(schedule.router, prefix="/api")
app.include_router(events.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Load Scheduler API is running."}