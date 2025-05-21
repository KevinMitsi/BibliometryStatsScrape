# Documentación del Sistema de Análisis Bibliométrico
# CADA MSVC TIENE UNA DOCUMENTACIÓN PROPIA PARA INFORMACIÓN MÁS DETALLADA LEERLO

## 📚 Visión General de la Aplicación

La aplicación es una solución full-stack para el scraping, procesamiento y visualización de artículos académicos. Incluye:

- **FastAPI Backend**: API RESTful para gestionar solicitudes de scraping y procesamiento de datos
- **Angular Frontend**: Interfaz de usuario para búsqueda y visualización
- **Docker Infrastructure**: Contenedores para los servicios
- **Data Processing Pipeline**: Convierte datos XML a JSON estructurado
- **Microservicios**: Componentes especializados para diferentes funcionalidades

---

## 🚀 API Principal - Endpoints

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

## 🔍 Microservicio Stats - Endpoints de Estadísticas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/stats` | GET | Get all statistics combined |
| `/stats/authors` | GET | Get top 15 first authors |
| `/stats/types` | GET | Get counts by publication type |
| `/stats/year_by_type` | GET | Get publications by year and type |
| `/stats/journals` | GET | Get top 15 journals |
| `/stats/publishers` | GET | Get top 15 publishers |
| `/stats/terms_by_category` | GET | Get frequency of terms by category |

### Endpoints de Visualización

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/stats/plot/types` | GET | Bar chart of publications by type |
| `/stats/plot/authors` | GET | Bar chart of top authors |
| `/stats/plot/year_by_type` | GET | Line chart of publications by year and type |
| `/stats/plot/journals` | GET | Bar chart of top journals |
| `/stats/plot/publishers` | GET | Bar chart of top publishers |
| `/stats/plot/wordcloud` | GET | Word cloud of keywords from abstracts |
| `/keywords/co-occurrence` | GET | Network visualization of keyword co-occurrences |

### Endpoints del Sistema

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |

---

## 📝 Microservicio msvc-texts - Procesamiento de Texto

### Overview

`msvc-texts` es un microservicio Spring Boot que procesa y analiza abstracts de textos de artículos académicos. Proporciona las siguientes funcionalidades:
* Recuperación de abstracts y títulos del servicio scrapper
* Eliminación de duplicados exactos
* Identificación de abstracts similares usando algoritmos de similitud de texto (similitud coseno e índice Jaccard)
* Agrupación de abstracts similares para análisis

### Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/texts/health` | GET | Health check endpoint. Respuesta: `"Running"` con estado 200 OK |
| `/texts/read` | GET | Recupera todos los abstracts desde la fuente. Respuesta: Lista de textos de abstract |
| `/texts/findSimilar` | GET | Encuentra y agrupa abstracts similares. Respuesta: Un mapa donde las claves son listas de títulos de documentos similares y los valores son las listas de abstracts correspondientes |

---

## 🧩 Arquitectura del Sistema

### Microservicio Stats

```
StatsMsvc/
├── main.py                    # Punto de entrada de la aplicación FastAPI
├── Dockerfile                 # Configuración de Docker
├── requirements.txt           # Dependencias Python
└── services/                  # Módulos de servicio
    ├── stats_service.py       # Análisis estadístico
    ├── graphs_service.py      # Generación de visualizaciones
    ├── keyword_service.py     # Análisis de palabras clave
    ├── word_cloud_builder.py  # Generación de nubes de palabras
    └── co_occurrence_builder.py # Análisis de redes de co-ocurrencia
```

### Microservicio msvc-texts

```
com.kevin.msvc_texts/
├── MsvcTextsApplication.java       # Main Spring Boot application
├── controller/
│   └── AbstractReaderController.java  # REST endpoints
├── DTO/
│   ├── RefItem.java                # Data model for reference items
│   └── RefItemResponse.java        # Response wrapper
├── http/
│   └── FeignScrapper.java          # Feign client for scrapper service
└── service/
    ├── AbstractReader.java         # Service interface
    └── impl/
        └── AbstractReaderService.java  # Implementation with text processing logic
```

### Proyecto Principal

```
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
```

---

## 🔧 Servicios Clave

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

### AbstractReader Service

El servicio implementa la funcionalidad principal del microservicio de texto:

#### Métodos clave:

1. **read()** - Recupera abstracts de la fuente de datos
```java
@Override
public List<String> read() {
    // Obtenemos los datos y eliminamos duplicados exactos
    List<RefItem> uniqueItems = removeDuplicates(feignScrapper.getAllItems().getData());
    return uniqueItems.stream()
            .map(RefItem::getAbstractText)
            .toList();
}
```

2. **Algoritmos de Similitud**

```java
// Umbrales de similitud
private static final double COSINE_THRESHOLD = 0.5;
private static final double JACCARD_THRESHOLD = 0.3;
```

---

## 🖥️ Frontend Angular

### BibliometryView

Este proyecto fue generado con [Angular CLI](https://github.com/angular/angular-cli) versión 14.2.13.

#### Servidor de desarrollo

Ejecuta `ng serve` para un servidor de desarrollo. Navega a `http://localhost:4200/`. La aplicación se recargará automáticamente si cambias alguno de los archivos fuente.

#### Construcción

Ejecuta `ng build` para construir el proyecto. Los artefactos de compilación se almacenarán en el directorio `dist/`.

---

## 📂 Almacenamiento de Datos

Archivos de datos importantes mantenidos por la aplicación:

- **`src/refs/`**: Archivos XML descargados
- **`repeated.json`**: Seguimiento de artículos duplicados
- **`xml_hashes.json`**: Hashes utilizados para deduplicación

---

## 🔄 Proceso de Lanzamiento (`launch.bat`)

Script de inicio automatizado:

- Activa el entorno virtual de Python (si existe)
- Instala dependencias desde `requirements.txt`
- Inicia servicios con Docker Compose
- Lanza la aplicación Angular
- Ejecuta el servidor FastAPI con Uvicorn
- Maneja limpieza al finalizar

---

## 🛠️ Instrucciones de Configuración

1. Asegúrate de tener instalados Docker, Python 3.x y Node.js
2. Clona el repositorio
3. Ejecuta `launch.bat` para iniciar todos los servicios
4. Accede al frontend en: `http://localhost:4200`
5. La API estará disponible en: `http://localhost:8000`

### Configuración de Docker para msvc-texts

```dockerfile
# Etapa 1: Builder - Compila la aplicación y sus dependencias
FROM maven:3.8.5-openjdk-17 AS builder
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests=true -e

# Etapa 2: Runtime
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8003
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Configuración de la Aplicación msvc-texts

```properties
spring.application.name=msvc-texts
server.port=8003
```

---

## 🔒 Notas de Seguridad

- Se requieren credenciales para acceder a bases de datos académicas
- Las credenciales se usan únicamente durante las búsquedas y no se almacenan
- En producción, asegúrate de que el acceso a la API esté autenticado

---

## 🔄 Integración con Otros Servicios

El microservicio msvc-texts está diseñado para trabajar con:
1. Un servicio scrapper (esperado en host.docker.internal:8000)
2. Una aplicación frontend (permitida desde varios orígenes en la configuración CORS)

El servicio recupera datos del servicio scrapper a través del endpoint `/convert` y los procesa para el análisis de similitud de texto.
