import json
import time
import random
from datetime import datetime, timedelta, timezone
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

TOPIC = "user_activity"
users = ["user_1", "user_2", "user_3", "user_4"]
pages = ["/home", "/products", "/cart", "/profile"]

print("Producing TIME-SERIES data to Kafka...")

# Start time: 10 minutes ago
start_time = datetime.now(timezone.utc) - timedelta(minutes=10)

for minute in range(15):
    current_base_time = start_time + timedelta(minutes=minute)
    print(f"--- Sending data for minute {minute} (Time: {current_base_time.isoformat()}) ---")
    
    for _ in range(10): # 10 events per minute
        user = random.choice(users)
        event_time = current_base_time + timedelta(seconds=random.randint(0, 59))
        
        # Random event
        event = {
            "event_time": event_time.isoformat(),
            "user_id": user,
            "page_url": random.choice(pages),
            "event_type": "page_view"
        }
        producer.send(TOPIC, event)

        # Occasional session start/end
        if random.random() < 0.3:
            producer.send(TOPIC, {
                "event_time": event_time.isoformat(),
                "user_id": user,
                "page_url": "/home",
                "event_type": "session_start"
            })
            
            # End session 2 minutes later
            producer.send(TOPIC, {
                "event_time": (event_time + timedelta(minutes=2)).isoformat(),
                "user_id": user,
                "page_url": "/logout",
                "event_type": "session_end"
            })
            
    producer.flush()
    time.sleep(1) # Wait a bit to let Spark process

print("Done generating data.")
