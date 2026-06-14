# backend/app/routers/events.py

from fastapi import APIRouter
from app.core.database import supabase

router = APIRouter()


@router.get("/events")
def get_events():
    """
    Returns full log of all deferral events, newest first.
    """
    response = supabase.table("schedule_events").select("*").order("timestamp", desc=True).execute()
    return response.data


@router.get("/stats")
def get_stats():
    """
    Returns KPI values for the 4 dashboard cards.
    """
    # Get latest load reading
    load_response = supabase.table("load_readings").select("*").order("timestamp", desc=True).limit(1).execute()
    latest = load_response.data[0] if load_response.data else {"total_load_w": 0, "within_limit": True}

    # Count deferred appliances today
    events_response = supabase.table("schedule_events").select("*").eq("action", "DEFERRED").execute()
    deferred_count = len(events_response.data)

    # Get peak limit from settings
    settings_response = supabase.table("settings").select("*").limit(1).execute()
    settings = settings_response.data[0] if settings_response.data else {"peak_limit_w": 4000, "billing_rate": 50}

    peak_limit = settings.get("peak_limit_w", 4000)
    billing_rate = settings.get("billing_rate", 50)

    # Simple cost saved estimate: each deferral saves ~800W for 2 hours
    cost_saved = round((deferred_count * 800 * 2 / 1000) * billing_rate, 2)

    return {
        "total_load_w": latest["total_load_w"],
        "deferred_count": deferred_count,
        "peak_limit_w": peak_limit,
        "cost_saved_rs": cost_saved,
        "within_limit": latest["within_limit"],
    }