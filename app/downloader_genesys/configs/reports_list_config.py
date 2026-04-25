SCHEDULES = {
    "HOURLY": {
        "type": "cron",
        "minute": 0,
        "hour": "8-22"
    },
    "EVERY_2H_ODD": {
        "type": "cron",
        "minute": 0,
        "hour": "9-21/2"
    },
    "EVERY_2H_EVEN": {
        "type": "cron",
        "minute": 0,
        "hour": "8-22/2"
    },
    "TEST": {
        "type": "cron",
        "minute": "*/1",
        "hour": "8-22/2"
    }
}

CONTACT_LISTS_CONFIG = [
    {
        "name": "C2C PV",
        "contact_list_id": "bf7b5827-68a3-487d-93f9-f7894fb9043d",
        "heavy": False,
        "schedule": SCHEDULES["HOURLY"],
        "type": "contact_list"
    },
    {
        "name": "C2C Prepago",
        "contact_list_id": "otro-id",
        "heavy": False,
        "schedule": SCHEDULES["HOURLY"],
        "type": "contact_list"
    },
]