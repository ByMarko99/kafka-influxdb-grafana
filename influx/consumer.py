# Import necessary libraries
from confluent_kafka import Consumer, KafkaException, KafkaError
from influxdb_client import InfluxDBClient, Point, WriteOptions
import json

# Kafka consumer configuration
conf = {
    'bootstrap.servers': '192.168.85.34:9092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Create Kafka consumer
consumer = Consumer(conf)
consumer.subscribe(['sensor-data'])

# Create InfluxDB client
influx_client = InfluxDBClient(
    url="your_ip",
    token="your_token",
    org="admin"
)
write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))

# Consume messages from Kafka and write to InfluxDB
try:
    while True:
        msg = consumer.poll(1.0)  # Wait for message for 1 second

        if msg is None:
            continue  # No message available in 1 second
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"End of partition reached {msg.partition()} at offset {msg.offset()}")
            else:
                raise KafkaException(msg.error())
        else:
            try:
                data = json.loads(msg.value().decode('utf-8'))
               # Create a point and write to InfluxDB
                point = Point("environment") \
                    .field("temperature", data["temperature"]) \
                    .field("humidity", data["humidity"]) \
                    .time(int(data["timestamp"] * 1e9))  # Convert timestamp to nanoseconds


                write_api.write(bucket="sensor_data", record=point)
                print(f"Stored: {data}")
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                print(f"Raw message: {msg.value().decode('utf-8')}")
except KeyboardInterrupt:
    pass
finally:
    consumer.close()