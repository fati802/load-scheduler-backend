# backend/app/services/optimization.py

import pandas as pd
from app.core.database import supabase
from datetime import datetime, timezone

PEAK_LIMIT = 4000  # Temporarily lowered to test deferrals (change back to 4000 after testing)

DEFERRABLE_MAP = {
    "AC": False,
    "Fridge": False,
    "Washer": True,
    "Lights": False,
    "Pump": True,
}


def greedy_scheduler(df: pd.DataFrame) -> pd.DataFrame:
    schedule = df.copy()
    schedule["hour"] = schedule["time"].apply(lambda t: int(float(t)))
    schedule["is_deferrable"] = schedule["appliance"].map(DEFERRABLE_MAP)

    for hour in sorted(schedule["hour"].unique()):
        hour_mask = schedule["hour"] == hour

        while True:
            active = schedule[hour_mask & (schedule["status"] == "ON")]
            total_load = active["power"].sum()

            if total_load <= PEAK_LIMIT:
                break

            deferrable = active[active["is_deferrable"] == True]

            if deferrable.empty:
                break

            idx = deferrable["priority"].idxmax()
            new_hour = (schedule.loc[idx, "hour"] + 2) % 24
            schedule.loc[idx, "hour"] = new_hour
            schedule.loc[idx, "status"] = "DEFERRED"

    return schedule


def push_schedule_to_supabase(schedule: pd.DataFrame):
    deferred = schedule[schedule["status"] == "DEFERRED"]

    events = []
    for _, row in deferred.iterrows():
        events.append({
            "appliance_name": row["appliance"],
            "action": "DEFERRED",
            "reason": f"Total load exceeded {PEAK_LIMIT}W at hour {int(row['hour'])}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    if events:
        supabase.table("schedule_events").insert(events).execute()
        print(f"[optimization] Pushed {len(events)} deferral events to Supabase.")
    else:
        print("[optimization] No deferrals — all loads within limit.")


def push_load_readings_to_supabase(schedule: pd.DataFrame):
    readings = []

    for hour in sorted(schedule["hour"].unique()):
        active = schedule[(schedule["hour"] == hour) & (schedule["status"] == "ON")]
        total = int(active["power"].sum())
        now = datetime.now(timezone.utc)
        ts = now.replace(hour=int(hour) % 24, minute=0, second=0, microsecond=0)
        readings.append({
            "timestamp": ts.isoformat(),
            "total_load_w": total,
            "within_limit": total <= PEAK_LIMIT,
        })

    if readings:
        supabase.table("load_readings").insert(readings).execute()
        print(f"[optimization] Pushed {len(readings)} load readings to Supabase.")


def run_optimization(csv_path: str = "schedule.csv"):
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    optimized = greedy_scheduler(df)
    push_load_readings_to_supabase(optimized)
    push_schedule_to_supabase(optimized)

    print("[optimization] Done.")
    return optimized