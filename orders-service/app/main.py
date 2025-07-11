from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from db import SessionLocal
from models import Order
from kafka_producer import send_stock_request, send_notification_event
import time

app = FastAPI()

class OrderIn(BaseModel):
    item: str = Field(..., min_length=1, description="Nombre del producto")
    quantity: int = Field(..., gt=0, description="Cantidad debe ser mayor que 0")

@app.post("/orders")
def create_order(order: OrderIn):
    db = SessionLocal()
    
    # Crear orden temporalmente
    new_order = Order(item=order.item, quantity=order.quantity)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Solicitar verificación de stock
    send_stock_request({
        "order_id": new_order.id,
        "item": new_order.item,
        "quantity": new_order.quantity
    })
    
    # Enviar notificación inmediata (como funcionaba antes)
    send_notification_event({
        "order_id": new_order.id,
        "item": new_order.item,
        "quantity": new_order.quantity
    })
    
    db.close()
    
    return {
        "message": "Order created and pending stock verification", 
        "order_id": new_order.id,
        "status": "pending"
    }

@app.get("/orders/{order_id}/status")
def get_order_status(order_id: int):
    db = SessionLocal()
    order = db.query(Order).filter_by(id=order_id).first()
    db.close()
    
    if order:
        return {
            "order_id": order_id,
            "status": "exists",
            "item": order.item,
            "quantity": order.quantity
        }
    else:
        return {
            "order_id": order_id,
            "status": "not_found"
        }

@app.get("/orders")
def get_all_orders():
    db = SessionLocal()
    orders = db.query(Order).all()
    db.close()
    
    return [{"id": order.id, "item": order.item, "quantity": order.quantity} for order in orders]