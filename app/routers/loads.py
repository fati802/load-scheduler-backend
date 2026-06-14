from fastapi import APIRouter
from app.core.database import supabase

router = APIRouter()


@router.get("/loads")
def get_loads():
    response = supabase.table("appliances").select("*").execute()
    return response.data


@router.get("/readings")
def get_readings():
    try:
        response = supabase.table("load_readings").select("*").order("timestamp", desc=False).execute()
        return response.data if response.data else []
    except Exception:
        return []