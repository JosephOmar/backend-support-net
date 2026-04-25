import httpx
import asyncio
from app.core.config import settings

client = httpx.AsyncClient(timeout=60)

# DOWNLOAD FROM ANALYTICS
async def create_export(payload):
    res = await client.post(
        f"{settings.GENESYS_BASE_URL}/analytics/reporting/exports",
        headers=settings.GENESYS_HEADERS,
        json=payload
    )

    if res.status_code != 200:
        raise Exception(f"Error export: {res.text}")

    return res.json()


async def get_export_by_id(export_id):
    res = await client.get(
        f"{settings.GENESYS_BASE_URL}/analytics/reporting/exports/{export_id}",
        headers=settings.GENESYS_HEADERS
    )
    if res.status_code == 404:
        return {"status": "PENDING"}
    
    if res.status_code != 200:
        raise Exception(f"Error get export: {res.text}")

    return res.json()

async def wait_for_export(export_id, timeout=1200, heavy=False):
    elapsed = 0
    interval = 10 if heavy else 5

    while elapsed < timeout:     
        data = await get_export_by_id(export_id)
        status = data.get("status")
        print(f"⏳ {export_id} → {status} ({elapsed}s)")
        if status == "COMPLETED":
            await asyncio.sleep(2)  # buffer extra
            return data

        if status == "FAILED":
            raise Exception(f"Export {export_id} falló")
        
        if status == "PENDING":
            print(f"⏳ {export_id} → aún no disponible")

        if status == "CANCELLED":
            raise Exception(f"Export {export_id} cancelado")

        await asyncio.sleep(interval)
        elapsed += interval

    raise TimeoutError(f"Timeout export {export_id} - elapsed {elapsed}")

# DOWNLOAD FROM LIST IN QUEUE
async def create_export_list(contact_list_id):
    url = f"{settings.GENESYS_BASE_URL}outbound/contactlists/{contact_list_id}/export"

    res = await client.get(url, headers=settings.GENESYS_HEADERS)
    return res.json()
    
async def check_export_status_list(contact_list_id):
    url = f"{settings.GENESYS_BASE_URL}/outbound/contactlists/{contact_list_id}/export"

    res = await client.get(url, headers=settings.GENESYS_HEADERS)
    return res.json()
    
