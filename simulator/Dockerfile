FROM python:3.10-slim

WORKDIR /app
RUN pip install paho-mqtt
COPY esp32_mock.py .

CMD ["python", "esp32_mock.py"]
