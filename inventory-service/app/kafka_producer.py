from confluent_kafka import Producer
import json, os

producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})

def send_stock_response(event_data):
    """Envía respuesta sobre disponibilidad de stock"""
    event = {"type": "stock_response", "data": event_data}
    producer.produce("stock-events", json.dumps(event).encode("utf-8"))
    producer.flush()
    print(f"Sent stock response: {event_data}")

def send_product_update(event_data):
    """Envía actualización de producto"""
    event = {"type": "product_update", "data": event_data}
    producer.produce("product-events", json.dumps(event).encode("utf-8"))
    producer.flush()
    print(f"Sent product update: {event_data}")