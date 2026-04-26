# services/users_service.py
from .genesys_client import genesys_request
import asyncio
from app.core.cache import cache
from app.core.config import settings
from app.proxy_genesys.core.status_config import STATUS_CONFIG

from datetime import datetime, timezone


def get_elapsed_seconds(date_str):
    if not date_str:
        return 0

    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    return int((now - dt).total_seconds())


def normalize_user(entity):
    user = entity.get("user", {})

    return {
        "name": user.get("name"),
        "presence": {
            "status": user.get("presence", {}).get("presenceDefinition", {}).get("systemPresence"),
            "time": user.get("presence", {}).get("modifiedDate"),
        },
        "routing": {
            "status": user.get("routingStatus", {}).get("status"),
            "time": user.get("routingStatus", {}).get("startTime"),
        }
    }


def evaluate_alerts(user):
    best_alert = None

    for config in STATUS_CONFIG:
        if config["source"] == "presence":
            status = user["presence"]["status"]
            time = user["presence"]["time"]

        elif config["source"] == "routing":
            status = user["routing"]["status"]
            time = user["routing"]["time"]
        else:
            continue

        if status != config["status"]:
            continue

        elapsed = get_elapsed_seconds(time)

        min_t = config.get("min_threshold", 0)
        max_t = config.get("max_threshold")

        level = None

        if config.get("visibility_only"):
            if min_t <= elapsed <= max_t:
                level = "info"

        elif max_t:
            if elapsed >= max_t:
                level = "critical"
            elif elapsed >= min_t:
                level = "warning"

        else:
            if elapsed >= min_t:
                level = "warning"

        if status == "Offline" and elapsed > 3600:
            continue

        if not level:
            continue

        alert = {
            "name": user["name"],
            "status": status,
            "status_name": config["status_name"],
            "source": config["source"],
            "elapsed": elapsed,
            "threshold": min_t,
            "level": level
        }

        # 🔥 PRIORIDAD
        priority = {"critical": 3, "warning": 2, "info": 1}

        if not best_alert or priority[level] > priority[best_alert["level"]]:
            best_alert = alert

    return [best_alert] if best_alert else []

def compute_stats(users):
    total = len(users)

    connected = sum(
        1 for u in users
        if u["presence"]["status"] and u["presence"]["status"] != "Offline"
    )

    return {
        "total": total,
        "connected": connected
    }

# 🔥 AQUÍ EL CAMBIO IMPORTANTE
async def get_queue_users(queue_id: str):
    cache_key = f"queue_data:{queue_id}"

    cached = cache.get(cache_key, settings.CACHE_TTL_USERS)
    if cached:
        return cached

    url = f"/routing/queues/{queue_id}/users"

    params = (
        f"?queueId={queue_id}"
        "&pageSize=100"
        "&pageNumber=1"
        "&joined=true"
        "&sortBy=name"
        "&sortOrder=asc"
        "&expand=routingStatus,primaryPresence,presence"
    )

    data = await genesys_request(
        "GET",
        url + params
    )

    users = []
    alerts = []

    for entity in data.get("entities", []):
        user = normalize_user(entity)
        users.append(user)

        alerts.extend(evaluate_alerts(user))

    result = {
        "users": users,
        "alerts": alerts,
        "stats": compute_stats(users)
    }

    cache.set(cache_key, result)

    return result


# 🔥 también limpio aquí
async def get_all_queues_users(queue_ids: list[str]):
    tasks = [get_queue_users(qid) for qid in queue_ids]
    results = await asyncio.gather(*tasks)

    return {
        queue_ids[i]: results[i]
        for i in range(len(queue_ids))
    }