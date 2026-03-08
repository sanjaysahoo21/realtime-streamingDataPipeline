import json
import os
import time
from datetime import datetime, timedelta, timezone
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
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
producer.close()
print("Done.")
