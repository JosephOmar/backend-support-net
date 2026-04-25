import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from app.downloader_genesys.configs.reports_config import REPORTS_CONFIG
from app.downloader_genesys.builders.payload_builder import build_payload
from app.downloader_genesys.services.genesys import create_export
from app.downloader_genesys.jobs.worker import process_export

scheduler = AsyncIOScheduler(timezone=timezone("America/Lima"))

background_tasks = []

async def run_single_report(config):
    print(f"🚀 Ejecutando {config['name']} | type={config.get('type')}")

    try:
        if config["type"] == "analytics":
            payload = build_payload(config)
            result = await create_export(payload)

            # 👇 NO esperar → background
            task = asyncio.create_task(process_export({
                "id": result["id"],
                "config": config
            }))
            background_tasks.append(task)

        elif config["type"] == "contact_list":
            # 👇 también en background
            task = asyncio.create_task(process_export({
                "config": config
            }))
            background_tasks.append(task)

        else:
            print(f"⚠️ Tipo desconocido: {config.get('type')}")

    except Exception as e:
        print(f"❌ Error en {config['name']}: {e}")

running_jobs = set()

async def run_reports_parallel(configs, limit=3):
    job_key = tuple(sorted(c["name"] for c in configs))

    if job_key in running_jobs:
        print(f"⚠️ Job {job_key} ya en ejecución")
        return

    running_jobs.add(job_key)

    try:
        semaphore = asyncio.Semaphore(limit)

        async def run_with_limit(config):
            async with semaphore:
                await run_single_report(config)  # 👈 ahora es rápido

        # 👇 solo lanza exports (rápido)
        await asyncio.gather(*(run_with_limit(c) for c in configs))

        # 👇 ahora sí esperas TODO el procesamiento real
        if background_tasks:
            print("⏳ Esperando procesos en background...")
            await asyncio.gather(*background_tasks)
            background_tasks.clear()

    finally:
        running_jobs.remove(job_key)


scheduler_started = False

def start_scheduler():
    global scheduler_started

    if scheduler_started:
        return

    print("🟢 Scheduler iniciado")

    grouped_jobs = {}

    for config in REPORTS_CONFIG:
        schedule = config.get("schedule")

        if not schedule:
            continue

        if schedule["type"] == "cron":
            key = (schedule.get("hour"), schedule.get("minute", 0))

            if key not in grouped_jobs:
                grouped_jobs[key] = []

            grouped_jobs[key].append(config)

    for (hour, minute), configs in grouped_jobs.items():
        print(f"⏰ Job programado → hour='{hour}' minute='{minute}' → {[c['name'] for c in configs]}")
        scheduler.add_job(
            run_reports_parallel,
            "cron",
            args=[configs, 3],
            hour=hour,
            minute=minute,
            max_instances=1
        )

    scheduler.start()
    scheduler_started = True