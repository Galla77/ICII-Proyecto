# 🎓 Sistema IoT Académico: ESP32 + Raspberry Pi + PC

Este proyecto es la demostración de un sistema IoT puro, funcional y robusto con comunicación bidireccional mediante el protocolo MQTT. No utiliza frameworks innecesarios ni bases de datos para mantener el despliegue extremadamente sencillo y libre de dependencias complejas.

## 🏗 Arquitectura del Sistema

*   **Publicador/Suscriptor (Nivel Físico):** Un **ESP32** (o dispositivo similar) que mide temperatura y publica el dato. También se suscribe a tópicos para encender un LED y controlar el tiempo de muestreo.
*   **Broker de Mensajes (Nivel de Red):** Una **Raspberry Pi** ejecutando el broker `mosquitto`. Es el servidor que enruta la mensajería MQTT de todos los participantes.
*   **Backend & Frontend (Nivel de Aplicación):** Tu **Computadora**. Ejecuta un servidor en `Flask` (Python) que:
    1.  Se conecta como cliente MQTT a la Raspberry y vigila las temperaturas.
    2.  Expone una API limpia (`GET`/`POST`) para la interfaz web.
    3.  Sirve estáticamente una Interfaz Web generada en HTML y Vanilla JS para interactuar en tiempo real.

---

## 🚀 Pasos para Ejecutar el Proyecto (En tu PC)

### Paso 1: Configurar el Entorno

Recomendamos usar un entorno virtual para no ensuciar el Python de tu sistema.

1.  Abre una terminal (Símbolo del sistema o PowerShell) en este directorio (`c:\Users\marco\Desktop\IC-II-Nuevo`).
2.  Crea el entorno virtual:
    ```bash
    python -m venv mi_entorno
    ```
3.  Activa el entorno (Windows):
    ```bash
    .\mi_entorno\Scripts\activate
    ```
    *(Sabrás que está activo si aparece `(mi_entorno)` en el prompt de comandos)*.

### Paso 2: Instalación de Dependencias

Con el entorno activado, instala las librerías base, que están listadas dentro de `requirements.txt`:
```bash
pip install -r requirements.txt
```
> Esto instalará `Flask` (para la web) y `paho-mqtt` (para hablar con la Raspberry).

### Paso 3: Configurar IP de la Raspberry Pi (Opcional pero muy importante)

Por defecto, el archivo `mqtt_handler.py` está configurado para conectarse al `localhost` (`127.0.0.1`).
**Si tu Broker Mosquitto está corriendo en la Raspberry Pi**, debes editar esto:

1.  Abre `mqtt_handler.py`
2.  En la última línea, donde se inicializa la variable del sistema:
    ```python
    mqtt_client = MQTTHandler(broker="192.168.1.100", port=1883)
    ```
    *(Reemplaza `192.168.1.100` con la IPv4 real de tu Raspberry Pi dentro de tu red local)*.

### Paso 4: ¡Correr el servidor!

En la terminal, ejecuta el archivo principal:
```bash
python app.py
```
> Si Windows te pide permisos de firewall, selecciona **Permitir acceso**.

### Paso 5: Abrir el Dashboard Interactivo

Abre tu navegador de preferencia (Chrome, Edge, Firefox) e ingresa a la dirección:
`http://localhost:5000`

Desde ahí podrás ver instantáneamente los cambios en caso de medir temperatura externa, encender remotamente el LED, o modificar los intervalos de trabajo de tu hardware.

---

## 📡 Diccionario de Tópicos (Topics) MQTT

| Tópico               | Sentido de los datos | Función principal | ¿Qué transfiere? |
|----------------------|----------------------|-------------------|------------------|
| `sensor/temperatura` | **ESP32 → PC**      | PC escucha periódicamente un valor enviado por el ESP32. | Un número flotante (`25.5`) o JSON. |
| `esp32/led`          | **PC → ESP32**      | PC manda comando para encender relé/LED a lo lejos. | Cadenas de texto: `"ON"` / `"OFF"`. |
| `esp32/config`       | **PC → ESP32**      | PC decide el tiempo de pausa (Delay) en el código del ESP. | Un entero de tiempo en ms (`"5000"`). |

## 📦 Estructura del Código
```
├── app.py                 <- Punto de entrada clásico de Flask. Une las URLs con la lógica Python.
├── mqtt_handler.py        <- Clase limpia de Paho-MQTT para conectar/desconectar sin ensuciar Flask.
├── requirements.txt       <- Sólo 2 requerimientos obligatorios.
├── README.md              <- Instrucciones.
├── templates/
│   └── index.html         <- La "Vista". Estructura HTML simple y semántica.
└── static/
    ├── style.css          <- Estética visual agradable, diseño oscuro (dark-mode), responsive puro.
    └── script.js          <- El "Controlador de Frontend": consume las APIs usando Fetch local.
```
