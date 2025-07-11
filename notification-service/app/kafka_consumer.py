from confluent_kafka import Consumer
import os, json
import requests

# 🔧 USAR VARIABLE DE ENTORNO EN LUGAR DE HARDCODEAR
MAILTRAP_TOKEN = os.getenv("MAILTRAP_TOKEN", "ac4cedd284b816a8da7acbe1bf7174f2")

def send_success_email(order_id, item, quantity):
    url = "https://sandbox.api.mailtrap.io/api/send/3882249"
    
    payload = {
        "from": {
            "email": "hello@example.com",
            "name": "Mailtrap Test"
        },
        "to": [
            {
                "email": "rnegretec@est.ups.edu.ec"
            }
        ],
        "subject": "✅ Orden Confirmada Exitosamente!",
        "text": f"¡Orden confirmada!\nOrden #{order_id} - Producto: {item} - Cantidad: {quantity}\n\nTu orden ha sido procesada correctamente.",
        "category": "Orden Exitosa"
    }
    
    headers = {
        "Authorization": f"Bearer {MAILTRAP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"SUCCESS email sent for order {order_id}! Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending success email: {e}")
        return False

def send_rejection_email(order_id, item, quantity, reason):
    url = "https://sandbox.api.mailtrap.io/api/send/3882249"
    
    # 🔍 PERSONALIZAR ASUNTO Y MENSAJE SEGÚN EL MOTIVO
    if "no existe" in reason.lower() or "not found" in reason.lower():
        subject = "❌ Orden Rechazada - Producto No Disponible"
        message = f"Orden rechazada\nOrden #{order_id} - Producto: {item} - Cantidad: {quantity}\n\nMotivo: {reason}\n\nEl producto solicitado no está disponible en nuestro catálogo."
    else:
        subject = "❌ Orden Rechazada - Stock Insuficiente"
        message = f"Orden rechazada\nOrden #{order_id} - Producto: {item} - Cantidad: {quantity}\n\nMotivo: {reason}\n\nNo tenemos suficiente stock para procesar tu orden."
    
    payload = {
        "from": {
            "email": "hello@example.com",
            "name": "Mailtrap Test"
        },
        "to": [
            {
                "email": "rnegretec@est.ups.edu.ec"
            }
        ],
        "subject": subject,
        "text": message,
        "category": "Orden Rechazada"
    }
    
    headers = {
        "Authorization": f"Bearer {MAILTRAP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"REJECTION email sent for order {order_id}! Status: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending rejection email: {e}")
        return False

consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    'group.id': 'notification-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(["notification-events"])
print("Notification service listening for notification events...")
print(f"Kafka servers: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')}")

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        print("Error:", msg.error())
        continue
    event = json.loads(msg.value().decode("utf-8"))
    print(f"Received event: {event}")
    
    if event["type"] == "confirm_order":
        data = event["data"]
        
        # 🔍 DECIDE QUÉ EMAIL ENVIAR BASADO EN EL STATUS
        if data.get("status") == "rejected":
            # ❌ ENVÍA EMAIL DE RECHAZO
            send_rejection_email(
                data["order_id"], 
                data["item"], 
                data["quantity"], 
                data.get("reason", "Stock insuficiente")
            )
        elif data.get("status") == "accepted":
            # ✅ ENVÍA EMAIL DE ÉXITO
            send_success_email(data["order_id"], data["item"], data["quantity"])
        else:
            print(f"Unknown status: {data.get('status')}")
