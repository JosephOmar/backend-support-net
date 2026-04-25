# routes/dashboard.py
from fastapi import APIRouter
from app.proxy_genesys.services.dashboard_service import get_dashboard_data
from app.proxy_genesys.core.queue_config import QUEUE_CONFIG

router = APIRouter()

@router.get("/dashboard")
async def dashboard():
    queue_ids = list(QUEUE_CONFIG.keys())
    return await get_dashboard_data(queue_ids)