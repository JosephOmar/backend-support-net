import asyncio
from app.downloader_genesys.services.genesys import wait_for_export, create_export_list, check_export_status_list
from app.downloader_genesys.services.downloader import download_file
from app.downloader_genesys.services.state import update_export_state, load_state
import time

fast_sem = asyncio.Semaphore(5)
slow_sem = asyncio.Semaphore(2)

async def process_export(export_info):
    config = export_info["config"]
    export_id = export_info.get("id")  # puede no existir en contact_list

    state = load_state()

    # 🔥 clave única por tipo
    state_key = export_id if export_id else f"list_{config.get('contact_list_id')}"

    if state_key in state and state[state_key] == "downloaded":
        print(f"⏩ {config['name']} ya descargado")
        return

    sem = slow_sem if config.get("heavy") else fast_sem

    async with sem:
        try:
            # =========================================
            # 🟢 ANALYTICS FLOW (lo que ya tienes)
            # =========================================
            if config["type"] == "analytics":
                export = await wait_for_export(
                    export_id,
                    timeout=config.get("timeout", 1200),
                    heavy=config.get("heavy", False)
                )

                download_url = export["downloadUrl"]

            # =========================================
            # 🔵 CONTACT LIST FLOW (nuevo)
            # =========================================
            elif config["type"] == "contact_list":
                await process_contact_list(config)
                return

            else:
                raise Exception(f"Tipo desconocido: {config.get('type')}")

            # =========================================
            # ⬇️ DESCARGA (común)
            # =========================================
            path = await download_file(
                download_url,
                config["name"]
            )

            update_export_state(state_key, "downloaded")

            print(f"✅ {config['name']} → {path}")

        except Exception as e:
            update_export_state(state_key, "error")
            print(f"❌ {config['name']} → {e}")

MIN_WAIT = 6      # más agresivo (antes 8)
MAX_WAIT = 18     # más corto que antes
POLL_INTERVAL = 2 # antes 3 → más rápido

async def process_contact_list(config):
    contact_list_id = config["contact_list_id"]
    name = config["name"]

    print(f"📋 Exportando lista: {name}")

    # 1. Estado inicial
    initial_data = await check_export_status_list(contact_list_id)
    initial_ts = initial_data.get("exportTimestamp")
    initial_uri = initial_data.get("uri")

    print(f"🕓 {name} timestamp inicial: {initial_ts}")

    # 2. Lanzar export
    await create_export_list(contact_list_id)
    print(f"🚀 {name} export lanzado")

    # 🔥 Pequeño delay inicial (clave)
    await asyncio.sleep(4)

    start_time = time.time()
    download_url = None

    last_valid_uri = initial_uri
    uri_missing_streak = 0  # 🔥 detectar regeneración real

    # 3. Polling
    for i in range(30):
        await asyncio.sleep(POLL_INTERVAL)

        try:
            data = await check_export_status_list(contact_list_id)
        except Exception as e:
            print(f"⚠️ {name} error consultando estado: {e}")
            continue

        ts = data.get("exportTimestamp")
        uri = data.get("uri")

        elapsed = int(time.time() - start_time)

        print(
            f"⏳ {name} intento {i+1} → ts={ts} | uri={'YES' if uri else 'NO'} | elapsed={elapsed}s"
        )

        # 🟢 Guardar última URL válida
        if uri:
            last_valid_uri = uri
            uri_missing_streak = 0
        else:
            uri_missing_streak += 1

        # ✅ NUEVO EXPORT LISTO
        if uri and ts and ts != initial_ts and elapsed >= MIN_WAIT:
            print(f"🆕 {name} nuevo export listo")
            download_url = uri
            break

        # 🧠 DETECCIÓN DE REGENERACIÓN REAL
        if uri_missing_streak >= 2:
            print(f"🔄 {name} regenerando export...")

        # ⚠️ FALLBACK INTELIGENTE
        if (
            elapsed >= MAX_WAIT
            and last_valid_uri
            and (
                uri_missing_streak < 3      # regeneración corta → espera
                or elapsed >= MAX_WAIT + 10 # regeneración larga → fallback igual
            )
        ):
            print(f"⚠️ {name} usando último export disponible")
            download_url = last_valid_uri
            break

    # 🔴 Timeout real
    if not download_url:
        print(f"⏱ {name} timeout sin export utilizable")
        return

    # 4. Descargar
    try:
        print(f"⬇️ Descargando {name}")
        path = await download_file(download_url, name)
        print(f"✅ {name} → {path}")

    except Exception as e:
        print(f"❌ {name} error descarga: {e}")