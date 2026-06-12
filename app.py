from flask import Flask, jsonify, request, render_template
from mqtt_handler import mqtt_client

app = Flask(__name__)

# Iniciamos el cliente MQTT de paho para que escuche en background
mqtt_client.start()

# ==========================================
# RUTAS DEL FRONTEND (Interfaz Web HTML/JS)
# ==========================================
@app.route("/")
def index():
    """Sirve la página web principal del dashboard."""
    # Flask busca automáticamente 'index.html' en la carpeta 'templates'
    return render_template("index.html")

# ==========================================
# ENDPOINTS REST API
# ==========================================
@app.route("/data", methods=["GET"])
def get_data():
    """Devuelve el último valor de temperatura capturado de MQTT en formato JSON."""
    return jsonify(mqtt_client.last_data)

@app.route("/led", methods=["POST"])
def set_led():
    """Recibe un comando desde el dashboard web y lo publica a MQTT."""
    data = request.json
    state = data.get("estado")
    
    if state in ["ON", "OFF"]:
        mqtt_client.publish_led(state)
        return jsonify({"status": "success", "message": f"Comando LED [{state}] enviado"}), 200
        
    return jsonify({"error": "Estado inválido. Use 'ON' o 'OFF'"}), 400

@app.route("/config", methods=["POST"])
def set_config():
    """Publica al ESP32 un nuevo intervalo de muestreo en ms."""
    data = request.json
    intervalo = data.get("intervalo")
    
    # Validamos que se envíe un número
    if intervalo and str(intervalo).isdigit():
        mqtt_client.publish_config(intervalo)
        return jsonify({"status": "success", "message": f"Intervalo {intervalo}ms enviado"}), 200
        
    return jsonify({"error": "Intervalo inválido. Debe ser un número."}), 400

@app.route("/api/history", methods=["GET"])
def get_history():
    """Devuelve el historial de datos desde Supabase."""
    limit = request.args.get("limit", default=50, type=int)
    
    if mqtt_client.supabase:
        try:
            # Obtener los últimos 'limit' registros, ordenados por created_at desc
            response = mqtt_client.supabase.table("sensor_data").select("*").order("created_at", desc=True).limit(limit).execute()
            # Invertimos la lista para que vengan en orden cronológico para el gráfico
            data = response.data[::-1]
            return jsonify(data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Supabase no configurado"}), 500


if __name__ == '__main__':
    # Ejecuta el servidor en '0.0.0.0' para que cualquier PC o celular
    # en la red local pueda entrar poniendo la IP de la computadora:5000
    # NOTA: use_reloader=False para impedir que MQTTHandler se inicie más de una vez en modo debug.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
