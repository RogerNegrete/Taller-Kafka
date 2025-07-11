from confluent_kafka import Consumer
import json, os
from db import SessionLocal
from models import Order
from kafka_producer import send_inventory_event, send_notification_event

consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    'group.id': 'orders-group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['stock-events'])
print("Orders service listening for stock events...")
print(f"Kafka servers: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')}")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("Error:", msg.error())
        continue
    
    event = json.loads(msg.value().decode("utf-8"))
    print(f"Orders received event: {event}")
    
    if event["type"] == "stock_response":
        data = event["data"]
        order_id = data["order_id"]
        
        # Update order status in database
        db = SessionLocal()
        order = db.query(Order).filter_by(id=order_id).first()
        
        if order:
            if data["available"]:  # ✅ HAY STOCK
                # Update order status to accepted
                order.status = "accepted"
                db.commit()
                
                # 📧 ENVÍA NOTIFICACIÓN DE ÉXITO
                send_notification_event({
                    "order_id": order_id,
                    "item": data["item"],
                    "quantity": data["quantity"],
                    "status": "accepted"
                })
                
                # 📦 ACTUALIZA EL STOCK
                send_inventory_event({
                    "order_id": order_id,
                    "item": data["item"],
                    "quantity": data["quantity"]
                })
            else:  # ❌ NO HAY STOCK
                # Update order status to rejected
                order.status = "rejected"
                db.commit()
                
                # 📧 ENVÍA NOTIFICACIÓN DE RECHAZO
                send_notification_event({
                    "order_id": order_id,
                    "item": data["item"],
                    "quantity": data["quantity"],
                    "status": "rejected",
                    "reason": data.get("error", "Stock insuficiente")
                })
        
        db.close()