import json
import os
import time
from datetime import datetime, timezone
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

TOPIC = "user_activity"

print("Producing SESSION TEST events to Kafka...")

# Session Start
event_start = {
    "event_time": datetime.now(timezone.utc).isoformat(),
    "user_id": "user_1",
    "page_url": "/home",
    "event_type": "session_start"
}
producer.send(TOPIC, event_start)
print("Sent:", event_start)

# Simulating session duration
time.sleep(5)

# Session End
event_end = {
    "event_time": datetime.now(timezone.utc).isoformat(),
    "user_id": "user_1",
    "page_url": "/logout",
    "event_type": "session_end"
}
producer.send(TOPIC, event_end)
print("Sent:", event_end)

producer.flush()
producer.close()
print("Done.")
