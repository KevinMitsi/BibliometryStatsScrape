# Etapa de construcción
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias de compilación
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Crear entorno virtual e instalar dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa final
FROM python:3.11-slim

WORKDIR /app

# Copiar el entorno virtual desde la etapa de construcción
COPY --from=builder /opt/venv /opt/venv

# Configurar PATH para usar el entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto 8001
EXPOSE 8001

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]