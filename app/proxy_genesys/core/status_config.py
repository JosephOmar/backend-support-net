STATUS_CONFIG = [
    {
        "status": "Meal",
        "source": "presence",
        "min_threshold": 60,
    },
    {
        "status": "Busy",
        "source": "presence",
        "min_threshold": 15,
        "max_threshold": 25,
    },
    {
        "status": "Offline",
        "source": "presence",
        "min_threshold": 1,
        "max_threshold": 5,
        "visibility_only": True
    }
]