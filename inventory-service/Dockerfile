FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app .

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]