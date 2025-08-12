from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from ..services import ai_client
import os

ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
es = Elasticsearch(ES_HOST)

router = APIRouter()

class AlertRequest(BaseModel):
    alert: dict

@router.get("/")
def list_alerts(limit: int = 10):
    """List recent alerts stored in Elasticsearch"""
    try:
        resp = es.search(
            index="alerts",
            size=limit,
            sort=[{"@timestamp": {"order": "desc"}}],
            query={"match_all": {}}
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/triage")
def triage_alert(req: AlertRequest):
    """Send alert to AI for classification and store result in ES"""
    try:
        ai_result = ai_client.classify_alert(req.alert.get("message", ""))
        doc = {
            "@timestamp": req.alert.get("@timestamp"),
            "raw": req.alert,
            "classification": ai_result.get("classification"),
            "reason": ai_result.get("reason"),
            "next_steps": ai_result.get("next_steps"),
            "ioc": ai_result.get("ioc"),
        }
        es.index(index="alerts", document=doc)
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
