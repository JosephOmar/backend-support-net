from datetime import datetime, timedelta, timezone
import pytz

def get_interval(minutes):
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=minutes)
    return f"{past.isoformat()}/{now.isoformat()}"

PERU_TZ = pytz.timezone("America/Lima")


def get_daily_interval_peru():
    now = datetime.now(PERU_TZ)

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    return f"{to_utc_iso(start)}/{to_utc_iso(end)}"


def get_hourly_interval_peru(minutes=60):
    now = datetime.now(PERU_TZ)

    end = now.replace(second=0, microsecond=0)
    start = end - timedelta(minutes=minutes)

    return f"{to_utc_iso(start)}/{to_utc_iso(end)}"


def to_utc_iso(dt):
    return dt.astimezone(pytz.utc).isoformat()