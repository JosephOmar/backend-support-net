from datetime import datetime
from app.downloader_genesys.utils.time_utils import (
    get_daily_interval_peru,
    get_hourly_interval_peru
)

BASE_PAYLOAD = {
    "timeZone": "America/Lima",
    "exportFormat": "CSV",
    "csvDelimiter": "COMMA",
    "locale": "es",
    "includeDurationFormatInHeader": False
}


def build_columns(columns):
    return [
        {"columnOrder": i + 1, "columnName": col}
        for i, col in enumerate(columns)
    ]


def resolve_interval(config):
    interval_type = config.get("interval_type", "daily")

    if interval_type == "daily":
        return get_daily_interval_peru()

    if interval_type == "hourly":
        minutes = config.get("interval_minutes", 60)
        return get_hourly_interval_peru(minutes)

    raise ValueError(f"Tipo de intervalo no soportado: {interval_type}")


def build_payload(config):
    payload = BASE_PAYLOAD.copy()

    # nombre dinámico
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    payload["name"] = f"{now} {config['name']}"

    payload["viewType"] = config["viewType"]

    # intervalo dinámico
    payload["interval"] = resolve_interval(config)

    # filtros
    payload["filter"] = config.get("filter", {})

    # columnas
    payload["selectedColumns"] = build_columns(config["columns"])

    # opcionales (solo si existen)
    OPTIONAL_FIELDS = ["durationFormat", "period"]

    for field in OPTIONAL_FIELDS:
        if field in config:
            payload[field] = config[field]

    return payload


def build_all_payloads(configs):
    return [build_payload(cfg) for cfg in configs]