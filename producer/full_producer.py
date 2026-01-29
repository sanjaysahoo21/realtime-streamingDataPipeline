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
event_types = ["page_view", "click"]

print("Producing FULL TRAFFIC to Kafka...")

for i in range(20):
    user = random.choice(users)
    # Start session
    producer.send(TOPIC, {
        "event_time": datetime.now(timezone.utc).isoformat(),
        "user_id": user,
        "page_url": "/home",
        "event_type": "session_start"
    })
    
    # Page views
    for _ in range(random.randint(1, 5)):
        producer.send(TOPIC, {
            "event_time": datetime.now(timezone.utc).isoformat(),
            "user_id": user,
            "page_url": random.choice(pages),
            "event_type": "page_view"
        })
        time.sleep(0.1)

    # End session
    producer.send(TOPIC, {
        "event_time": datetime.now(timezone.utc).isoformat(),
        "user_id": user,
        "page_url": "/logout",
        "event_type": "session_end"
    })
    print(f"Sent session for {user}")
    time.sleep(1)

producer.flush()
print("Done.")
