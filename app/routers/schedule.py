# backend/app/routers/schedule.py

from fastapi import APIRouter
from app.core.database import supabase
from app.services.optimization import run_optimization

router = APIRouter()


@router.get("/schedule")
def get_schedule():
    """
    Returns all schedule events from the database.
    """
    response = supabase.table("schedule_events").select("*").order("timestamp", desc=True).execute()
    return response.data


@router.post("/schedule/run")
def run_schedule():
    """
    Triggers the optimization algorithm.
    Reads schedule.csv, runs greedy scheduler, pushes results to Supabase.
    """
    run_optimization(csv_path="schedule.csv")
    return {"message": "Optimization complete. Results pushed to Supabase."}