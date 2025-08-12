# backend/app/services/ai_client.py
import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_alert(alert_text):
    prompt = f"""You are a SOC analyst. Classify the alert as Benign, Suspicious, or Critical.
Alert:
{alert_text}
Respond in JSON: {{ "classification": "...", "reason": "...", "next_steps": ["..."] }}"""
    resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0)
    return resp["choices"][0]["message"]["content"]
