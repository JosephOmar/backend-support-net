import httpx
from app.core.config import settings

_token_cache = {
    "access_token": None,
    "expires_at": 0
}

async def get_access_token():
    import time

    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://login.mypurecloud.com/oauth/token",
            auth=(settings.CLIENT_ID, settings.CLIENT_SECRET),
            data={"grant_type": "client_credentials"}
        )

    data = response.json()

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data["expires_in"] - 60

    return _token_cache["access_token"]