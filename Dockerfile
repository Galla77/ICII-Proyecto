FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto donde corre Flask
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
