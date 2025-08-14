import os
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import openai
from collections import defaultdict

ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
INDEX_NAME = "alerts"

es = Elasticsearch(ES_HOST)

openai.api_key = os.getenv("OPENAI_API_KEY")

LOOKBACK_MINUTES = 15

def fetch_recent_alerts():
    now = datetime.utcnow()
    since = now - timedelta(minutes=LOOKBACK_MINUTES)

    query = {
        "query": {
            "range": {
                "@timestamp": {
                    "gte": since.isoformat() + "Z"
                }
            }
        },
        "size": 500,
        "sort": [{"@timestamp": {"order": "desc"}}]
    }

    res = es.search(index=INDEX_NAME, body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]

def detect_campaigns(alerts):
    campaigns = defaultdict(list)
    for alert in alerts:
        if alert.get("campaign_id"):
            campaigns[alert["campaign_id"]].append(alert)
    return {cid: evts for cid, evts in campaigns.items() if len(evts) > 1}

def summarize_campaign(campaign_id, events):
    stages = [e.get("stage") for e in events if e.get("stage")]
    src_ip = events[0].get("src_ip")
    users = set(e.get("user") for e in events if e.get("user"))
    return f"Campaign {campaign_id}: Source {src_ip}, Users {', '.join(users)}, Stages: {', '.join(stages)}"

def ai_classify(alert):
    # Add campaign awareness
    context = ""
    if alert.get("campaign_id"):
        context += f"This alert is part of campaign {alert['campaign_id']}.\n"

    prompt = f"""
You are a SOC analyst AI. Classify the severity of this alert and explain why.

Alert details:
Timestamp: {alert['@timestamp']}
Message: {alert['message']}
Service: {alert['service']}
Source IP: {alert['src_ip']}
Country: {alert['country']}
User: {alert['user']}
Stage: {alert.get('stage')}
{context}

Severity levels: LOW, MEDIUM, HIGH, CRITICAL.
If part of a campaign, increase severity.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful SOC analyst AI."},
            {"role": "user", "content": prompt}
        ]
    )
    return resp.choices[0].message["content"]

def main():
    alerts = fetch_recent_alerts()
    campaigns = detect_campaigns(alerts)

    if campaigns:
        print("\n=== Coordinated Campaigns Detected ===")
        for cid, evts in campaigns.items():
            print(summarize_campaign(cid, evts))

    print("\n=== Alert Classifications ===")
    for alert in alerts:
        classification = ai_classify(alert)
        print(f"[{alert['@timestamp']}] {alert['message']} -> {classification}")

if __name__ == "__main__":
    main()
