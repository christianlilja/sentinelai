import os
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_alert(alert_text: str):
    """Classify an alert as Benign, Suspicious, or Critical using GPT"""
    prompt = f"""
You are a SOC analyst. Classify the alert as Benign, Suspicious, or Critical.
Extract any IOCs (IPs, domains, hashes).
Respond in JSON with keys: classification, reason, ioc, next_steps.

Alert:
{alert_text}
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    try:
        return json.loads(resp["choices"][0]["message"]["content"])
    except json.JSONDecodeError:
        return {"classification": "Unknown", "reason": "Parsing error", "ioc": [], "next_steps": []}

def translate_hunt_query(nl_query: str):
    """Translate a natural language hunt query into Elasticsearch DSL"""
    prompt = f"""
You are a translator from analyst English to Elasticsearch Query DSL.
Return only JSON with a valid Elasticsearch query.

Analyst request:
{nl_query}
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resp["choices"][0]["message"]["content"]
