# backend/app/routers/loads.py

from fastapi import APIRouter
from app.core.database import supabase

router = APIRouter()


@router.get("/loads")
def get_loads():
    """
    Returns current status of all 5 appliances from the database.
    """
    response = supabase.table("appliances").select("*").execute()
    return response.data