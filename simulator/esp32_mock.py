import paho.mqtt.client as mqtt
import json
import time
import random
import os

# IP del broker configurada por variable de entorno (por defecto mosquitto en docker)
BROKER_IP = os.environ.get("MQTT_BROKER", "mosquitto")
PORT = 1883
TOPIC = "sensor/dht11"

print(f"Simulador ESP32 iniciando... Conectando a MQTT: {BROKER_IP}:{PORT}")

client = mqtt.Client()

# Intentar conectar con reintentos
while True:
    try:
        client.connect(BROKER_IP, PORT, 60)
        print("Simulador conectado al broker MQTT.")
        break
    except Exception as e:
        print(f"Esperando al broker MQTT... ({e})")
        time.sleep(3)

client.loop_start()

base_temp = 25.0
base_hum = 50.0

try:
    while True:
        # Generar datos simulados con pequeña variación
        base_temp += random.uniform(-0.5, 0.5)
        base_hum += random.uniform(-1.0, 1.0)
        
        # Limites razonables
        base_temp = max(15.0, min(35.0, base_temp))
        base_hum = max(30.0, min(80.0, base_hum))

        payload = {
            "temp": round(base_temp, 2),
            "hum": round(base_hum, 2)
        }
        
        # Publicar mensaje
        client.publish(TOPIC, json.dumps(payload))
        print(f"Publicado en {TOPIC}: {payload}")
        
        # Publicar cada 5 segundos
        time.sleep(5)
except KeyboardInterrupt:
    print("Simulador detenido.")
finally:
    client.loop_stop()
    client.disconnect()
