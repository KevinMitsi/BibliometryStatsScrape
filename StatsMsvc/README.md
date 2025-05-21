# Documentación API Stats

## Endpoints de Estadísticas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/stats` | GET | Get all statistics combined |
| `/stats/authors` | GET | Get top 15 first authors |
| `/stats/types` | GET | Get counts by publication type |
| `/stats/year_by_type` | GET | Get publications by year and type |
| `/stats/journals` | GET | Get top 15 journals |
| `/stats/publishers` | GET | Get top 15 publishers |
| `/stats/terms_by_category` | GET | Get frequency of terms by category |

## Endpoints de Visualización

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/stats/plot/types` | GET | Bar chart of publications by type |
| `/stats/plot/authors` | GET | Bar chart of top authors |
| `/stats/plot/year_by_type` | GET | Line chart of publications by year and type |
| `/stats/plot/journals` | GET | Bar chart of top journals |
| `/stats/plot/publishers` | GET | Bar chart of top publishers |
| `/stats/plot/wordcloud` | GET | Word cloud of keywords from abstracts |
| `/keywords/co-occurrence` | GET | Network visualization of keyword co-occurrences |

## Endpoints del Sistema

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |

## Arquitectura

Este microservicio está diseñado para trabajar junto a otros servicios en un sistema de análisis bibliométrico:
* Conecta con un servicio de scraper de datos (esperado en `http://host.docker.internal:8000/convert`)
* Procesa y analiza los datos obtenidos
* Proporciona tanto datos estadísticos en bruto (JSON) como visualizaciones (imágenes PNG)

## Requisitos

Las dependencias clave incluyen:
* FastAPI - Framework web
* Pandas - Análisis de datos
* Matplotlib - Visualización
* NetworkX - Análisis de grafos para redes de co-ocurrencia
* WordCloud - Generación de nubes de palabras
* Requests - Cliente HTTP para obtención de datos

Consulta requirements.txt para la lista completa de dependencias.

## Desarrollo

### Estructura del Proyecto
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