from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LoadReading(BaseModel):
    total_load_w: int
    within_limit: bool

class ScheduleEvent(BaseModel):
    appliance_name: str
    action: str
    reason: Optional[str] = None

class ScheduleRecord(BaseModel):
    time: float
    appliance: str
    power: int
    status: str
    is_deferrable: bool
    priority: int

class ApplianceBase(BaseModel):
    name: str
    power_w: int
    priority: int
    is_deferrable: bool

class Settings(BaseModel):
    peak_limit_w: int
    billing_rate: float
    timezone: str