from confluent_kafka import Producer
import json, os

producer = Producer({'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})

def send_order_event(order_data):
    event = {"type": "order_created", "data": order_data}
    producer.produce("order-events", json.dumps(event).encode("utf-8"))
    producer.flush()
    print(f"Sent order event: {order_data}")

def send_stock_request(request_data):
    event = {"type": "stock_request", "data": request_data}
    producer.produce("stock-requests", json.dumps(event).encode("utf-8"))
    producer.flush()
    print(f"Sent stock request: {request_data}")

def send_inventory_event(event_data):
    event = {"type": "update_stock", "data": event_data}
    producer.produce("inventory-events", json.dumps(event).encode("utf-8"))
    producer.flush()
    print(f"Sent inventory event: {event_data}")

def send_notification_event(event_data):
    event = {"type": "confirm_order", "data": event_data}
    producer.produce("notification-events", json.dumps(event).encode("utf-8"))
    producer.flush()
    print(f"Sent notification event: {event_data}")