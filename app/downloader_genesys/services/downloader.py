import httpx
from pathlib import Path
import asyncio
from datetime import datetime
from app.core.config import settings

download_sem = asyncio.Semaphore(3)

async def download_file(url, name, retries=5):
    async with download_sem:

        async with httpx.AsyncClient(timeout=60) as client:

            for attempt in range(retries):
                res = await client.get(
                    url,
                    headers=settings.GENESYS_HEADERS,
                    follow_redirects=False
                )

                # 🔥 manejar redirect manual
                if res.status_code == 303:
                    redirect_url = res.headers.get("Location")

                    if not redirect_url:
                        raise Exception("Redirect sin Location")

                    # 🔥 segunda llamada SIN headers
                    file_res = await client.get(redirect_url)

                    if file_res.status_code == 200 and file_res.content:
                        settings.DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

                        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        path = settings.DOWNLOAD_PATH / filename

                        with open(path, "wb") as f:
                            f.write(file_res.content)

                        return str(path)

                    print(f"⚠️ Redirect fallido: {file_res.status_code}")

                else:
                    print(f"⚠️ Intento {attempt+1} fallido")
                    print(f"Status: {res.status_code}")

                await asyncio.sleep(2)

        raise Exception("Error descargando archivo tras redirects")