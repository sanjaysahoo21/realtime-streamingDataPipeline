import json
import time
from datetime import datetime, timedelta, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

TOPIC = "user_activity"
future_time = datetime.now(timezone.utc) + timedelta(minutes=30)

print(f"Sending FINALIZER event at {future_time.isoformat()} to force close windows...")

producer.send(TOPIC, {
    "event_time": future_time.isoformat(),
    "user_id": "finalizer_user",
    "page_url": "/admin",
    "event_type": "heartbeat"
})

producer.flush()
print("Done.")
