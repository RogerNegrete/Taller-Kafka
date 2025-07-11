#!/bin/bash

# Ejecuta el consumidor en segundo plano
python kafka_consumer.py &

# Ejecuta la app FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000
