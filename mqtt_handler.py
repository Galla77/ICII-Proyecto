import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class MQTTHandler:
    def __init__(self, broker="10.1.6.2", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Estado en memoria para guardar el último valor recibido
        self.last_data = {
            "temperatura": None,
            "timestamp": None
        }

        # Configuración de Supabase
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key) if url and key else None

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Conectado al broker MQTT exitosamente")
            # Nos suscribimos al topic del sensor de temperatura
            self.client.subscribe("sensor/#")
        else:
            print(f"Error al conectar al broker. Código: {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")
        print(f"Mensaje recibido [{topic}]: {payload}")
        
        if topic == "sensor/dht11":
            try:
                data = json.loads(payload)

                temp = float(data.get("temp"))
                hum = float(data.get("hum"))

                self.last_data["temperatura"] = temp
                self.last_data["humedad"] = hum
                self.last_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insertar en Supabase
                if self.supabase:
                    try:
                        self.supabase.table("sensor_data").insert({
                            "temperatura": temp,
                            "humedad": hum
                        }).execute()
                        print("Datos guardados en Supabase")
                    except Exception as e_supa:
                        print(f"Error al guardar en Supabase: {e_supa}")

            except Exception as e:
                print(f"Error al procesar datos: {e}")

    def start(self):
        """Inicia la conexión y deja el cliente corriendo en background."""
        try:
            self.client.connect(self.broker, self.port, 60)
            # loop_start maneja la recepción de mensajes en otro hilo (thread),
            # evitando bloquear el servidor REST (Flask).
            self.client.loop_start() 
        except Exception as e:
            print(f"Advertencia: No se pudo conectar al broker MQTT: {e}")
            print("Asegúrate de que el broker de Mosquitto esté iniciado y la IP sea correcta.")

    def publish_led(self, state):
        """Publica al ESP32 que prenda o apague un LED."""
        self.client.publish("esp32/led", state)
        
    def publish_config(self, interval):
        """Publica al ESP32 para cambiar el delay en cada toma de muestra."""
        # Se envía como string, el ESP32 debe convertirlo a int.
        self.client.publish("esp32/config", str(interval))

# Instancia global compartida para que interaccione con las rutas de Flask
broker_ip = os.environ.get("MQTT_BROKER", "mosquitto")
mqtt_client = MQTTHandler(broker=broker_ip, port=1883)
