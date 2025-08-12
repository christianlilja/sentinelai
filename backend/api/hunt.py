from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from ..services import ai_client
import os
import json

ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
es = Elasticsearch(ES_HOST)

router = APIRouter()

class HuntRequest(BaseModel):
    query: str

@router.post("/")
def hunt(req: HuntRequest):
    """Convert natural language hunt query to ES DSL and return results"""
    try:
        es_query = ai_client.translate_hunt_query(req.query)
        # If LLM returns string JSON, load it
        if isinstance(es_query, str):
            es_query = json.loads(es_query)
        resp = es.search(index="*", size=10, query=es_query.get("query", {}))
        return {
            "query": es_query,
            "results": [hit["_source"] for hit in resp["hits"]["hits"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
