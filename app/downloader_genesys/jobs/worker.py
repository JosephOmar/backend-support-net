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

MIN_WAIT = 8       # tiempo mínimo antes de aceptar resultado
MAX_WAIT = 25      # tiempo máximo antes de fallback
POLL_INTERVAL = 5  # menos agresivo (evita rate limit)


async def safe_check_export_status(contact_list_id, name):
    try:
        data = await check_export_status_list(contact_list_id)
        return data or {}

    except Exception as e:
        print(f"⚠️ {name} error consultando estado: {e}")
        return {}


async def process_contact_list(config):
    contact_list_id = config["contact_list_id"]
    name = config["name"]

    print(f"📋 Exportando lista: {name}")

    # -----------------------------
    # 1. Estado inicial
    # -----------------------------
    initial_data = await safe_check_export_status(contact_list_id, name)

    initial_uri = initial_data.get("uri")
    print(f"🕓 {name} uri inicial: {'YES' if initial_uri else 'NO'}")

    # -----------------------------
    # 2. Lanzar export
    # -----------------------------
    post_data = await create_export_list(contact_list_id, name)
    print(f"🧪 POST RESULT {name}: {post_data}")

    # 🔥 Delay inicial importante
    await asyncio.sleep(5)

    start_time = time.time()
    download_url = None

    last_valid_uri = initial_uri
    empty_response_streak = 0

    # -----------------------------
    # 3. Polling inteligente
    # -----------------------------
    for i in range(20):  # menos intentos = menos rate limit
        await asyncio.sleep(POLL_INTERVAL)

        data = await safe_check_export_status(contact_list_id, name)

        ts = data.get("exportTimestamp")
        uri = data.get("uri")

        elapsed = int(time.time() - start_time)

        print(
            f"⏳ {name} intento {i+1} → ts={ts} | uri={'YES' if uri else 'NO'} | elapsed={elapsed}s"
        )

        # -----------------------------
        # 🟢 Guardar última URL válida
        # -----------------------------
        if uri:
            last_valid_uri = uri
            empty_response_streak = 0
        else:
            empty_response_streak += 1

        # -----------------------------
        # ✅ EXPORT LISTO (sin depender de timestamp)
        # -----------------------------
        if uri and elapsed >= MIN_WAIT:
            print(f"🆕 {name} export listo")
            download_url = uri
            break

        # -----------------------------
        # ⚠️ POSIBLE RATE LIMIT / EXPORT EN PROGRESO
        # -----------------------------
        if not ts and not uri:
            print(f"⚠️ {name} sin datos (posible rate limit o en proceso)")

        # -----------------------------
        # ⚠️ FALLBACK CONTROLADO
        # -----------------------------
        if elapsed >= MAX_WAIT and last_valid_uri:
            print(f"⚠️ {name} usando último export disponible (fallback)")
            download_url = last_valid_uri
            break

    # -----------------------------
    # 🔴 Timeout real
    # -----------------------------
    if not download_url:
        print(f"⏱ {name} timeout sin export utilizable")
        return

    # -----------------------------
    # 4. Descargar
    # -----------------------------
    try:
        print(f"⬇️ Descargando {name}")
        path = await download_file(download_url, name)
        print(f"✅ {name} → {path}")

    except Exception as e:
        print(f"❌ {name} error descarga: {e}")