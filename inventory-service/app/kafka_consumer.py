from confluent_kafka import Consumer
import json, os
from db import SessionLocal
from models import Product
from kafka_producer import send_stock_response

consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    'group.id': 'inventory-group',
    'auto.offset.reset': 'earliest'
})

# Escucha eventos de inventory-events y stock-requests
consumer.subscribe(['inventory-events', 'stock-requests'])
print("Inventory service listening for inventory and stock request events...")
print(f"Kafka servers: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')}")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("Error:", msg.error())
        continue
    
    event = json.loads(msg.value().decode("utf-8"))
    print(f"Inventory received event: {event}")
    
    # Responder a solicitudes de stock
    if event["type"] == "stock_request":
        print(f"Processing stock request for order {event['data']['order_id']}")
        data = event["data"]
        db = SessionLocal()
        product = db.query(Product).filter_by(name=data["item"]).first()
        
        if product:
            available = product.stock >= data["quantity"]
            print(f"Product {data['item']} found. Stock: {product.stock}, Requested: {data['quantity']}, Available: {available}")
            send_stock_response({
                "order_id": data["order_id"],
                "item": data["item"],
                "quantity": data["quantity"],
                "available": available,
                "current_stock": product.stock
            })
        else:
            print(f"Product {data['item']} not found")
            send_stock_response({
                "order_id": data["order_id"],
                "item": data["item"],
                "quantity": data["quantity"],
                "available": False,
                "current_stock": 0,
                "error": "Product not found"
            })
        db.close()
    
    # Actualizar stock cuando la orden es confirmada
    elif event["type"] == "update_stock":
        data = event["data"]
        db = SessionLocal()
        product = db.query(Product).filter_by(name=data["item"]).first()
        if product and product.stock >= data["quantity"]:
            product.stock -= data["quantity"]
            db.commit()
            print(f"Stock updated for {product.name}: {product.stock}")
        else:
            print("Insufficient stock or product not found")
        db.close()