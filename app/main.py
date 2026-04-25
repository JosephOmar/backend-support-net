from fastapi import FastAPI, APIRouter, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.downloader_genesys.jobs.scheduler import start_scheduler
from app.downloader_genesys.jobs.scheduler import run_reports_parallel
from app.downloader_genesys.configs.reports_config import REPORTS_CONFIG

from app.proxy_genesys.routers import analytics, users
from app.proxy_genesys.services.dashboard_service import get_dashboard_data
from app.proxy_genesys.routers import analytics, users, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://gtr-net-support.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

@router.get("/test-run")
async def test_run():
    await run_reports_parallel(REPORTS_CONFIG)
    return {"status": "ok"}

app.include_router(router)
app.include_router(analytics.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")