import json
import time
import random
from datetime import datetime, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

TOPIC = "user_activity"


users = ["user_1", "user_2", "user_3", "user_4"]
pages = ["/home", "/products", "/cart", "/profile"]
event_types = ["page_view", "click", "session_start", "session_end"]

print("Producing events to Kafka...")

while True:
    event = {
        "event_time": datetime.now(timezone.utc).isoformat(),
        "user_id": random.choice(users),
        "page_url": random.choice(pages),
        "event_type": random.choice(event_types)
    }

    producer.send(TOPIC, event)
    print("Sent:", event)

    time.sleep(2)
