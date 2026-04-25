# services/genesys_client.py
import httpx
from app.core.config import settings

async def genesys_request(method: str, url: str, json=None):
    async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
        response = await client.request(
            method,
            f"{settings.GENESYS_BASE_URL}{url}",
            headers=settings.GENESYS_HEADERS,
            json=json
        )

        response.raise_for_status()
        return response.json()