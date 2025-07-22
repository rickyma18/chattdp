# Usa una imagen ligera oficial de Python
FROM python:3.11-slim

# Evita buffering y cache innecesario
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Crea directorio de trabajo
WORKDIR /app

# Copia dependencias primero (mejor cache)
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY assistant_service.py .

# Puerto por el que servimos (Cloud Run lo inyecta, pero lo exponemos por claridad)
ENV PORT=8080

# Comando de arranque
CMD ["python", "assistant_service.py"]
