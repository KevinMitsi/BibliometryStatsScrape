# 📚 Bibliometric Analysis Application Documentation

Este documento proporciona una visión general de la arquitectura, los endpoints, los servicios y el proceso de configuración de la aplicación de Análisis Bibliométrico.

---

## 📋 Application Overview

La aplicación es una solución full-stack para el scraping, procesamiento y visualización de artículos académicos. Incluye:

- **FastAPI Backend**: API RESTful para gestionar solicitudes de scraping y procesamiento de datos
- **Angular Frontend**: Interfaz de usuario para búsqueda y visualización
- **Docker Infrastructure**: Contenedores para los servicios
- **Data Processing Pipeline**: Convierte datos XML a JSON estructurado

---

## 🚀 API Endpoints

| Endpoint     | Method | Descripción                                                  | Request Body                                       | Response                      |
|--------------|--------|--------------------------------------------------------------|---------------------------------------------------|-------------------------------|
| `/scrape`    | POST   | Realiza scraping de artículos según criterios de búsqueda    | `{ search_string, email, password, top_results }` | `{ status, data }`           |
| `/convert`   | GET    | Convierte archivos XML existentes en el directorio `refs/`   | None                                              | `{ status, data }`           |
| `/repeated`  | GET    | Devuelve información sobre artículos duplicados detectados   | None                                              | `{ status, data, message }`  |
| `/health`    | GET    | Endpoint de verificación del estado del servicio             | None                                              | `{ status: "ok" }`           |


### 📦 Ejemplo de solicitud

```json
POST /scrape
{
  "search_string": "machine learning",
  "email": "user@example.com",
  "password": "password123",
  "top_results": 50
}
```
---

## 🔧 Services

### 🕸️ Scrapper Service

Servicio de scraping personalizado para obtener artículos académicos:

- **Ubicación**: `src/services/scrapper_service.py`
- **Funcionalidad**:
  - Autenticación en bases de datos académicas
  - Búsqueda de artículos según consulta del usuario
  - Descarga de datos en formato XML
  - Almacenamiento en el directorio `src/refs/`

### 🔄 Conversion Service

Servicio para transformar XML a JSON estructurado:

- **Ubicación**: `src/services/conversor.py`
- **Clase Principal**: `XmlToJsonConverter`
- **Funcionalidad**:
  - Analiza archivos XML en `refs/`
  - Extrae metadatos relevantes
  - Convierte los datos a formato JSON
  - Detecta y gestiona entradas duplicadas

---

## 📂 Data Storage

Archivos de datos importantes mantenidos por la aplicación:

- **`src/refs/`**: Archivos XML descargados
- **`repeated.json`**: Seguimiento de artículos duplicados
- **`xml_hashes.json`**: Hashes utilizados para deduplicación

---

## 🔄 Launch Process (`launch.bat`)

Script de inicio automatizado:

- Activa el entorno virtual de Python (si existe)
- Instala dependencias desde `requirements.txt`
- Inicia servicios con Docker Compose
- Lanza la aplicación Angular
- Ejecuta el servidor FastAPI con Uvicorn
- Maneja limpieza al finalizar

---

## 🛠️ Setup Instructions

1. Asegúrate de tener instalados Docker, Python 3.x y Node.js
2. Clona el repositorio
3. Ejecuta `launch.bat` para iniciar todos los servicios
4. Accede al frontend en: `http://localhost:4200`
5. La API estará disponible en: `http://localhost:8000`

---

## 🔒 Security Notes

- Se requieren credenciales para acceder a bases de datos académicas
- Las credenciales se usan únicamente durante las búsquedas y no se almacenan
- En producción, asegúrate de que el acceso a la API esté autenticado

---

## 🧱 Technical Architecture

### `launch.bat`

```text
launch.bat
├── Activa el entorno virtual de Python (si existe)
├── Instala dependencias desde requirements.txt
├── Inicia servicios con Docker Compose
├── Lanza el frontend Angular (ng serve)
├── Inicia el backend FastAPI con Uvicorn
└── Maneja la limpieza al cerrar
---

## Project Structure

bibliometric-analysis/
├── main.py                 # Aplicación FastAPI
├── launch.bat             # Script de inicio
├── requirements.txt       # Dependencias de Python
├── docker-compose.yml     # Configuración de contenedores
└── src/                   # Código fuente
    ├── __init__.py
    ├── repeated.json      # Registro de artículos duplicados
    ├── xml_hashes.json    # Hashes para deduplicación
    ├── refs/              # Archivos XML descargados
    └── services/          # Módulos de servicio
        ├── __init__.py
        ├── conversor.py         # Conversión XML a JSON
        └── scrapper_service.py  # Servicio de scraping




