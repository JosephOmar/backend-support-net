# services/analytics_service.py
from .genesys_client import genesys_request
from app.core.cache import cache
from app.core.config import settings


async def get_queue_metrics(queue_ids: list[str]):
    cache_key = f"metrics:{','.join(sorted(queue_ids))}"

    cached = cache.get(cache_key, settings.CACHE_TTL_METRICS)
    if cached:
        return cached

    payload = {
        "filter": {
            "type": "and",
            "clauses": [
                {
                    "type": "or",
                    "predicates": [
                        {
                            "type": "dimension",
                            "dimension": "queueId",
                            "value": qid
                        } for qid in queue_ids
                    ]
                },
                {
                    "type": "or",
                    "predicates": [
                        {
                            "type": "dimension",
                            "dimension": "mediaType",
                            "value": "voice"
                        }
                    ]
                }
            ]
        },
        "metrics": ["oWaiting", "oInteracting"],
        "groupBy": ["queueId", "mediaType"]
    }

    # ✅ sin token
    data = await genesys_request(
        "POST",
        "/analytics/queues/observations/query",
        json=payload
    )

    result = {}

    for group in data.get("results", []):
        # 🔥 importante: filtrar solo voice
        if group.get("group", {}).get("mediaType") != "voice":
            continue

        qid = group["group"]["queueId"]

        interacting = 0
        waiting = 0

        for metric in group.get("data", []):
            if metric["metric"] == "oInteracting":
                interacting = metric["stats"]["count"]
            elif metric["metric"] == "oWaiting":
                waiting = metric["stats"]["count"]

        result[qid] = {
            "interacting": interacting,
            "waiting": waiting
        }

    cache.set(cache_key, result)

    for qid in queue_ids:
        if qid not in result:
            result[qid] = {
                "interacting": 0,
                "waiting": 0
            }

    return result