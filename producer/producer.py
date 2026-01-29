import json
import time
from datetime import datetime, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
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
print("Done.")
