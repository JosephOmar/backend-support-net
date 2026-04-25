# core/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    GENESYS_BASE_URL = os.getenv(
        "GENESYS_BASE_URL",
        "https://api.mypurecloud.com/api/v2"
    )

    GENESYS_TOKEN = os.getenv("GENESYS_TOKEN")

    CACHE_TTL_METRICS = int(os.getenv("CACHE_TTL_METRICS", 30))
    CACHE_TTL_USERS = int(os.getenv("CACHE_TTL_USERS", 60))

    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", 10))

    DOWNLOAD_PATH = Path.home() / "Downloads"
    STATE_FILE = os.getenv("STATE_FILE", "./state.json")

    ENV = os.getenv("ENV", "dev")

    @property
    def GENESYS_HEADERS(self):
        if not self.GENESYS_TOKEN:
            raise ValueError("❌ GENESYS_TOKEN no está configurado")

        token = self.GENESYS_TOKEN

        if not token.startswith("Bearer "):
            token = f"Bearer {token}"

        return {
            "Authorization": token,
            "Content-Type": "application/json"
        }

settings = Settings()