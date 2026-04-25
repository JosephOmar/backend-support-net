# services/dashboard_service.py

from .users_service import get_all_queues_users
from .analytics_service import get_queue_metrics
from app.proxy_genesys.core.queue_config import QUEUE_CONFIG
import asyncio


async def get_dashboard_data(queue_ids: list[str]):
    # 🔥 llamadas en paralelo (perfecto esto)
    users_data, metrics_data = await asyncio.gather(
        get_all_queues_users(queue_ids),
        get_queue_metrics(queue_ids)
    )

    response = []

    for qid in queue_ids:
        queue_info = users_data.get(qid, {})

        alerts = queue_info.get("alerts", [])

        stats = queue_info.get("stats", [])

        response.append({
            "queueId": qid,
            "name": QUEUE_CONFIG.get(qid, {}).get("name", "Unknown"),
            "alerts": alerts,
            "stats": stats,
            "metrics": metrics_data.get(qid, {
                "interacting": 0,
                "waiting": 0
            })
        })

    return response