# simulator/generate_logs.py (very small sample)
from elasticsearch import Elasticsearch
import random, time, json
es = Elasticsearch("http://elastic:9200")

def make_auth_event():
    return {
        "@timestamp": "2025-08-11T12:34:56Z",
        "event": "ssh_auth",
        "user": random.choice(["alice","bob","root"]),
        "success": random.choice([True, False, False]),
        "src_ip": f"203.0.113.{random.randint(1,250)}",
    }

while True:
    es.index(index="auth-logs", body=make_auth_event())
    time.sleep(0.5)
