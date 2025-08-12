# /alerts -> GET alerts or POST new alert for triage
GET  /alerts?status=all&limit=50
POST /alerts/triage
  body: { "alert": { ... } }

# /hunt -> POST natural language hunt
POST /hunt
  body: { "query": "show me failed ssh logins from non-us ip's in the last 24h" }

# /ioc -> GET/POST IOC exports
GET  /ioc?alert_id=123
POST /ioc/export  -> { "format": "csv" }
