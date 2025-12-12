# Imagen base con Python
FROM python:3.13-slim

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de la API
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto donde correrá FastAPI
EXPOSE 8000

# Comando para correr la API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
