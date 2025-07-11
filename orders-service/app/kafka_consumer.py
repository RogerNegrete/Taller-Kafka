from confluent_kafka import Consumer
import json, os
from db import SessionLocal
from models import Order
from kafka_producer import send_inventory_event, send_notification_event

# Diccionario compartido para órdenes pendientes
pending_orders = {}

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
        print(f"Processing stock response for order {order_id}")
        
        if data["available"]:
            # Stock disponible - procesar orden
            print(f"Stock available for order {order_id}")
            
            # Actualizar stock
            send_inventory_event({
                "order_id": order_id,
                "item": data["item"],
                "quantity": data["quantity"]
            })
            
            # Enviar notificación de orden exitosa
            send_notification_event({
                "order_id": order_id,
                "item": data["item"],
                "quantity": data["quantity"],
                "status": "success"
            })
            
            print(f"Order {order_id} confirmed - Stock available")
            
        else:
            # Stock insuficiente - cancelar orden
            print(f"Order {order_id} cancelled - {data.get('error', 'Insufficient stock')}")
            
            # Enviar notificación de orden rechazada
            send_notification_event({
                "order_id": order_id,
                "item": data["item"],
                "quantity": data["quantity"],
                "status": "rejected",
                "reason": data.get('error', 'Stock insuficiente')
            })
            
            # Eliminar orden de la base de datos
            db = SessionLocal()
            order = db.query(Order).filter_by(id=order_id).first()
            if order:
                db.delete(order)
                db.commit()
            db.close()