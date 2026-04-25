from copy import deepcopy

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

REPORTS_OUT_CONFIG = {
  "durationFormat": "seconds",
  "interval_type": "daily",
  "viewType": "CAMPAIGN_INTERACTION_DETAIL_VIEW",
  "heavy": True,
  "schedule": SCHEDULES["EVERY_2H_ODD"],
  "type": "analytics",
  "filter": {
    "mediaTypes": ["voice"],
    "answered": True,
    "canonicalContactIds": [],
    "conversationIds": [],
    "externalContactIds": [],
    "externalOrgIds": [],
    "groupIds": []
  },
  "columns": [
            "interaction_view_conversation_id",
            "interaction_view_media_type",
            "interaction_view_user",
            "interaction_view_date",
            "interaction_view_end_date",
            "interaction_view_duration",
            "interaction_view_dnis",
            "interaction_view_queue",
            "interaction_view_division",
            "interaction_view_last_wrap_up",
            "interaction_view_disconnect_type",
            "interaction_view_wrap_up_segments",
            "interaction_view_total_talk_time",
            "interaction_view_total_handle",
            "interaction_view_mos",
            "interaction_view_direction",
            "interaction_view_remote",
            "interaction_view_wrap_up_code"
    ]
}

CAMPAIGNS_OUT = {
    "OUT1": "7d8d62c7-6ce4-4709-85bf-07ab2883fe92",
    "OUT2": "cd971757-9a86-4ffa-9c76-c6168f92562d",
    "OUT3": "70b6eb44-1b6d-4f94-b048-b047cf7261a8",
    "IVR": "72d5a804-706a-475d-b4b2-d368f572043b",
}

def build_report_out_config(name, campaign_id):
    config = deepcopy(REPORTS_OUT_CONFIG)

    config["name"] = name
    config["filter"]["outboundCampaignIds"] = [campaign_id]

    return config

REPORTS_OUT_CONFIG = [
    build_report_out_config(name, cid)
    for name, cid in CAMPAIGNS_OUT.items()
]

CONTACT_LIST_CONFIG = [
    {
        "name": "C2C Privado",
        "contact_list_id": "393c7afe-4f6d-43e8-be11-d05e30045ba4",
        "heavy": False,
        "schedule": SCHEDULES["HOURLY"],
        "type": "contact_list"
    },
    {
        "name": "RMKT Privado",
        "contact_list_id": "ad830fc7-2b2d-4142-8b3e-db515aa20489",
        "heavy": False,
        "schedule": SCHEDULES["HOURLY"],
        "type": "contact_list"
    },
    {
        "name": "C2C Publico",
        "contact_list_id": "ad830fc7-2b2d-4142-8b3e-db515aa20489",
        "heavy": False,
        "schedule": SCHEDULES["HOURLY"],
        "type": "contact_list"
    },
    {
        "name": "RMKT Publico",
        "contact_list_id": "2cd03a48-a1d8-4c03-a815-f5fd12050364",
        "heavy": False,
        "schedule": SCHEDULES["HOURLY"],
        "type": "contact_list"
    },
]

REPORTS_CONFIG = [
    {
        "name": "Rendimiento C2C PV",
        "durationFormat": "milliseconds",
        "interval_type": "daily",
        "period": "PT30M",      
        "viewType": "QUEUE_PERFORMANCE_DETAIL_VIEW",
        "heavy": False,
        "schedule": SCHEDULES["HOURLY"],
        "type": "analytics",
        "filter": {
            "mediaTypes": ["voice"],
            "queueIds": ["0fd68d9a-be6d-4878-b743-3591f6d9eafc"],
            "canonicalContactIds": [],
            "externalContactIds": [],
            "externalOrgIds": []
        },
        "columns": [
            "queue_performance_view_interval_start",
            "queue_performance_view_offer",
            "queue_performance_view_answer",
            "queue_performance_view_abandon",
            "queue_performance_view_asa",
            "queue_performance_view_service_level_percent",
            "queue_performance_view_wait_average",
            "queue_performance_view_handle_average",
            "queue_performance_view_talk_average",
            "queue_performance_view_hold_average",
            "queue_performance_view_acw_average",
            "queue_performance_view_hold",
            "queue_performance_view_transfer",
        ]
    }, 
    {
        "name": "Status de Agentes",
        "durationFormat": "milliseconds",
        "interval_type": "daily",     
        "viewType": "AGENT_STATUS_SUMMARY_VIEW",
        "heavy": False,
        "schedule": SCHEDULES["EVERY_2H_ODD"],
        "type": "analytics",
        "filter": {
            "userState": "Active",
        },
        "columns": [
            "agent_status_view_agent_name",
            "agent_status_view_agent_name",
            "agent_status_logged_in",
            "agent_status_on_queue",
            "agent_status_idle",
            "agent_status_available",
            "agent_status_busy",
            "agent_status_away",
            "agent_status_break",
            "agent_status_meal",
            "agent_status_meeting",
            "agent_status_training",
            "agent_status_off_queue",
            "agent_status_interacting",
            "agent_status_view_login",
            "agent_status_view_logout",
        ]
    }, 
    *CONTACT_LIST_CONFIG,
    *REPORTS_OUT_CONFIG
]