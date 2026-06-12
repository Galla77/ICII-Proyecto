/**
 * 1. POLLING DE DATOS DEL SENSOR
 * Hace un GET al endpoint /data de Flask cada 2 segundos.
 */
async function fetchSensorData() {
    try {
        const response = await fetch('/data');
        if (!response.ok) throw new Error("Error en red local");

        const data = await response.json();
        
        // Solo actualizamos si hemos recibido algo válido por MQTT
        if (data.temperatura !== null) {
            const tempValueElement = document.getElementById('temp-value');
            tempValueElement.textContent = data.temperatura.toFixed(1);
            document.getElementById('temp-time').textContent = `Última actualización: ${data.timestamp}`;
            
            // Un pequeño efecto para mostrar si sube o baja la temperatura
            if (data.temperatura > 30) {
                tempValueElement.style.color = "#ef4444"; // Rojo si hace mucho calor
            } else if (data.temperatura < 15) {
                tempValueElement.style.color = "#3b82f6"; // Azul si hace frío
            } else {
                tempValueElement.style.color = "#10b981"; // Verde normal
            }
            
            // Actualizar gráficos en tiempo real
            updateChartsRealTime(data.temperatura, data.humedad, data.timestamp);
        }
    } catch (error) {
        console.error("Error obteniendo datos del sensor:", error);
    }
}

// Iniciar polling (primero inmediatamente, luego con setInterval)
fetchSensorData();
setInterval(fetchSensorData, 2000);

/**
 * 2. ENVÍO DE COMANDOS DEL LED
 * Hace POST a /led con { "estado": "ON" o "OFF" }
 */
async function controlLed(estado) {
    const statusMsg = document.getElementById('led-status');
    statusMsg.textContent = "⚙️ Procesando...";
    statusMsg.style.color = "#94a3b8"; // Gris neutro

    try {
        const response = await fetch('/led', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estado: estado })
        });

        const result = await response.json();
        if (response.ok) {
            statusMsg.textContent = `✅ Comando de LED [${estado}] enviado vía MQTT.`;
            statusMsg.style.color = "#10b981"; // Verde success
        } else {
            statusMsg.textContent = `❌ Error: ${result.error}`;
            statusMsg.style.color = "#ef4444"; // Rojo error
        }
    } catch (error) {
        statusMsg.textContent = "❌ Error de comunicación con el backend (PC).";
        statusMsg.style.color = "#ef4444";
        console.error(error);
    }
}

/**
 * 3. CONFIGURACIÓN DE FRECUENCIA
 * Hace POST a /config con { "intervalo": N }
 */
async function updateConfig() {
    const input = document.getElementById('interval-input');
    const statusMsg = document.getElementById('config-status');
    const interval = parseInt(input.value);

    // Validación lado cliente
    if (isNaN(interval) || interval < 500) {
        statusMsg.textContent = "⚠️ Ingresa un número válido (Mín: 500 ms).";
        statusMsg.style.color = "#ef4444";
        return;
    }

    statusMsg.textContent = "⚙️ Enviando configuración...";
    statusMsg.style.color = "#94a3b8";

    try {
        const response = await fetch('/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ intervalo: interval })
        });

        const result = await response.json();
        if (response.ok) {
            statusMsg.textContent = `✅ Frecuencia alterada a ${interval}ms vía MQTT.`;
            statusMsg.style.color = "#10b981";
            input.value = ""; // Limpiar caja
        } else {
            statusMsg.textContent = `❌ Error: ${result.error}`;
            statusMsg.style.color = "#ef4444";
        }
    } catch (error) {
        statusMsg.textContent = "❌ Error de comunicación con el backend (PC).";
        statusMsg.style.color = "#ef4444";
        console.error(error);
    }
}

/**
 * 4. GRÁFICOS CON CHART.JS
 */
let tempChartInstance = null;
let humChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    loadHistory(); // Carga inicial
});

function initCharts() {
    const ctxTemp = document.getElementById('tempChart').getContext('2d');
    const ctxHum = document.getElementById('humChart').getContext('2d');
    
    // Opciones globales de Chart.js para modo oscuro
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = '#334155';
    
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }
        },
        scales: {
            x: {
                ticks: { maxRotation: 45, minRotation: 45 }
            }
        },
        animation: {
            duration: 400 // Animaciones más rápidas
        }
    };

    tempChartInstance = new Chart(ctxTemp, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Temperatura (°C)', data: [], borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 2 }] },
        options: commonOptions
    });

    humChartInstance = new Chart(ctxHum, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Humedad (%)', data: [], borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', borderWidth: 2, fill: true, tension: 0.3, pointRadius: 2 }] },
        options: commonOptions
    });
}

// Carga el historial desde la base de datos (Supabase) a través de Flask
async function loadHistory() {
    const limit = document.getElementById('history-limit').value;
    try {
        const response = await fetch(`/api/history?limit=${limit}`);
        if (!response.ok) throw new Error("Error obteniendo historial");
        
        const data = await response.json();
        
        // Formatear etiquetas de tiempo a HH:MM:SS
        const labels = data.map(row => {
            const date = new Date(row.created_at);
            return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`;
        });
        const temps = data.map(row => row.temperatura);
        const hums = data.map(row => row.humedad);
        
        tempChartInstance.data.labels = labels;
        tempChartInstance.data.datasets[0].data = temps;
        tempChartInstance.update();
        
        humChartInstance.data.labels = labels;
        humChartInstance.data.datasets[0].data = hums;
        humChartInstance.update();
        
    } catch (error) {
        console.error("Error al cargar historial:", error);
    }
}

// Actualiza los gráficos en vivo agregando un solo punto y removiendo el más antiguo
let lastTimestamp = "";
function updateChartsRealTime(temp, hum, timestamp) {
    if (!tempChartInstance || !humChartInstance || timestamp === lastTimestamp) return;
    lastTimestamp = timestamp;

    const limit = parseInt(document.getElementById('history-limit').value);
    
    // Extraer solo la hora (HH:MM:SS) del timestamp "YYYY-MM-DD HH:MM:SS"
    const timeLabel = timestamp.split(" ")[1];

    // Temperatura
    tempChartInstance.data.labels.push(timeLabel);
    tempChartInstance.data.datasets[0].data.push(temp);
    if (tempChartInstance.data.labels.length > limit) {
        tempChartInstance.data.labels.shift();
        tempChartInstance.data.datasets[0].data.shift();
    }
    tempChartInstance.update('none'); // Update sin animación pesada
    
    // Humedad
    humChartInstance.data.labels.push(timeLabel);
    humChartInstance.data.datasets[0].data.push(hum);
    if (humChartInstance.data.labels.length > limit) {
        humChartInstance.data.labels.shift();
        humChartInstance.data.datasets[0].data.shift();
    }
    humChartInstance.update('none');
}
