import network
import time
import machine
import dht
import json
from umqttsimple import MQTTClient

# =========================
# WIFI
# =========================

SSID = "UNRaf_Libre"
PASSWORD = "unraf2021"

# =========================
# MQTT
# =========================

# ¡ATENCIÓN! Cambia esta IP por la IP real de tu Raspberry Pi
MQTT_BROKER = "IP_DE_TU_RASPBERRY_PI"
CLIENT_ID = "ESP32Client"

TOPIC_PUB = b"sensor/dht11"
TOPIC_LED = b"esp32/led"
TOPIC_CONFIG = b"esp32/config"

# =========================
# HARDWARE
# =========================

LED_PIN = 2
DHT_PIN = 4

led = machine.Pin(LED_PIN, machine.Pin.OUT)
sensor = dht.DHT11(machine.Pin(DHT_PIN))

# =========================
# VARIABLES
# =========================

intervalo = 3000
last_read = 0

# =========================
# WIFI
# =========================

def conectar_wifi():

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if not wifi.isconnected():

        print("Conectando WiFi...")

        wifi.connect(SSID, PASSWORD)

        while not wifi.isconnected():
            time.sleep(0.5)

    print("WiFi conectado")
    print(wifi.ifconfig())

# =========================
# CALLBACK MQTT
# =========================

def callback(topic, msg):

    global intervalo

    topic = topic.decode()
    msg = msg.decode()

    print("Mensaje recibido:", topic, msg)

    # LED en tiempo real
    if topic == "esp32/led":

        if msg == "ON":
            led.value(1)
            print("LED ON")

        elif msg == "OFF":
            led.value(0)
            print("LED OFF")

    # cambiar intervalo dinámico
    elif topic == "esp32/config":

        try:
            nuevo = int(msg)

            if nuevo >= 1000:
                intervalo = nuevo
                print("Nuevo intervalo:", intervalo)

        except:
            print("Intervalo inválido")

# =========================
# MQTT
# =========================

def conectar_mqtt():

    client = MQTTClient(CLIENT_ID, MQTT_BROKER)

    client.set_callback(callback)

    client.connect()

    client.subscribe(TOPIC_LED)
    client.subscribe(TOPIC_CONFIG)

    print("MQTT conectado")

    return client

# =========================
# MAIN LOOP
# =========================

conectar_wifi()
client = conectar_mqtt()

while True:

    try:

        # 🟢 siempre escuchando MQTT (LED en tiempo real)
        client.check_msg()

        now = time.ticks_ms()

        # 🔵 sensor solo cada intervalo
        if time.ticks_diff(now, last_read) > intervalo:

            sensor.measure()

            temp = sensor.temperature()
            hum = sensor.humidity()

            payload = json.dumps({
                "temp": temp,
                "hum": hum
            })

            print("Publicando:", payload)
            client.publish(TOPIC_PUB, payload)

            last_read = now

    except Exception as e:
        print("Error:", e)

    time.sleep_ms(100)