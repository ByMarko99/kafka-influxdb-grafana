from confluent_kafka import Producer
import random
import time
import json

producer = Producer({'bootstrap.servers': '192.168.85.34:9092'})

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def generate_data():
    while True:
        data = {
            "temperature": round(random.uniform(20.0, 30.0), 2),
            "humidity": round(random.uniform(40.0, 60.0), 2),
            "timestamp": time.time()
        }
        # Serialize the data dictionary to a JSON-formatted string
        data_json = json.dumps(data)
        producer.produce('sensor-data', value=data_json, callback=delivery_report)
        producer.flush()
        time.sleep(1)

if __name__ == "__main__":
    generate_data()