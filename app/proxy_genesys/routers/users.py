# routes/users.py
from fastapi import APIRouter
from app.proxy_genesys.services.users_service import get_queue_users, get_all_queues_users

router = APIRouter()

@router.get("/users/{queue_id}")
async def users(queue_id: str):
    return await get_queue_users(queue_id)


@router.post("/users")
async def users_bulk(body: dict):
    queue_ids = body.get("queueIds", [])
    return await get_all_queues_users(queue_ids)