# routes/analytics.py
from fastapi import APIRouter
from app.proxy_genesys.services.analytics_service import get_queue_metrics

router = APIRouter()

@router.post("/metrics")
async def metrics(body: dict):
    queue_ids = body.get("queueIds", [])
    return await get_queue_metrics(queue_ids)