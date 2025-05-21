from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic_settings import BaseSettings
import requests
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from services.stats_service import generate_all_stats
from services.co_occurrence_builder import (
    generate_keyword_network,
    render_figure_to_bytes,
)
from services.graphs_service import (
    generate_authors_plot,
    generate_year_by_type_plot,
    generate_journals_plot,
    generate_publishers_plot,
    generate_stats_plot,
)
from services.word_cloud_builder import generate_overall_wordcloud

SCRAPER_URL = "http://host.docker.internal:8000/convert"



class StatsRequest(BaseSettings):
    pass

app = FastAPI(title="Statistics Microservice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200",
        "http://bibliometry-view",
        "http://bibliometry-view:80",
        "http://host.docker.internal:4200"],
    allow_credentials=True,
    allow_methods=["*"],      # GET, POST, PUT, DELETE…
    allow_headers=["*"],  # Content-Type, Authorization…
)




def fetch_json_data() -> List[Dict[str, Any]]:
    try:
        resp = requests.get(SCRAPER_URL)
        resp.raise_for_status()
        data = resp.json().get('data', [])
        if not isinstance(data, list):
            raise ValueError("Invalid data format: expected list of records")
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch data: {e}")


@app.get(
    "/stats",
    summary="Get all statistics")
def all_stats():
    json_list = fetch_json_data()
    stats = generate_all_stats(json_list)
    return {"status": "ok", "stats": stats}


@app.get(
    "/stats/authors",
    summary="Top 15 first authors")
def stats_authors():
    json_list = fetch_json_data()
    return {"status": "ok", "top_authors": generate_all_stats(json_list)['top_authors']}


@app.get(
    "/stats/types",
    summary="Counts by product type")
def stats_types():
    json_list = fetch_json_data()
    return {"status": "ok", "by_type": generate_all_stats(json_list)['by_type']}


@app.get(
    "/stats/year_by_type",
    summary="Publications by year and type")
def stats_year_by_type():
    json_list = fetch_json_data()
    return {"status": "ok", "year_by_type": generate_all_stats(json_list)['year_by_type']}


@app.get(
    "/stats/journals",
    summary="Top 15 journals")
def stats_journals():
    json_list = fetch_json_data()
    return {"status": "ok", "top_journals": generate_all_stats(json_list)['top_journals']}


@app.get(
    "/stats/publishers",
    summary="Top 15 publishers")
def stats_publishers():
    json_list = fetch_json_data()
    return {"status": "ok", "top_publishers": generate_all_stats(json_list)['top_publishers']}
def _plot_endpoint(plot_func):
    try:
        data = fetch_json_data()
        fig = plot_func(data)
        img_bytes = render_figure_to_bytes(fig)
        return StreamingResponse(img_bytes, media_type="image/png")
    except Exception as e:
        import logging
        logging.error(f"Error generating plot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")

@app.get(
    "/stats/plot/types",
    summary="Gráfico de barras: publicaciones por tipo de producto",
    response_description="PNG con gráfico de barras por tipo de producto"
)
def plot_by_type():
    return _plot_endpoint(generate_stats_plot)

@app.get(
    "/stats/plot/authors",
    summary="Gráfico de barras: Top primeros autores",
    response_description="PNG con gráfico de barras de top primeros autores"
)
def plot_top_authors():
    return _plot_endpoint(generate_authors_plot)

@app.get(
    "/stats/plot/year_by_type",
    summary="Gráfico de líneas: publicaciones por año y tipo",
    response_description="PNG con gráfico de líneas por año y tipo"
)
def plot_year_by_type():
    return _plot_endpoint(generate_year_by_type_plot)

@app.get(
    "/stats/plot/journals",
    summary="Gráfico de barras: Top revistas",
    response_description="PNG con gráfico de barras de top revistas"
)
def plot_top_journals():
    return _plot_endpoint(generate_journals_plot)

@app.get(
    "/stats/plot/publishers",
    summary="Gráfico de barras: Top editoriales",
    response_description="PNG con gráfico de barras de top editoriales"
)
def plot_top_publishers():
    return _plot_endpoint(generate_publishers_plot)


@app.get(
    "/stats/plot/wordcloud",
    summary="Nube de palabras general",
    response_description="PNG con la nube de palabras combinada"
)
def plot_overall_wordcloud():
    json_list = fetch_json_data()
    abstracts = [item.get("abstract", "") for item in json_list]

    fig = generate_overall_wordcloud(abstracts)

    img_bytes = render_figure_to_bytes(fig)
    return StreamingResponse(img_bytes, media_type="image/png")


@app.get("/keywords/co-occurrence",
         summary="Visualización de red de co-ocurrencia de keywords",
         response_description="Imagen PNG con la red de co-ocurrencia")
def keywords_network_visualization():
    try:
        # 1. Obtener datos
        json_list = fetch_json_data()

        # 2. Extraer abstracts asegurando que sean strings
        abstracts = []
        for item in json_list:
            abstract = item.get('abstract', '')
            # Convertir a string si no lo es
            if isinstance(abstract, dict):
                abstract = str(abstract)
            abstracts.append(abstract)

        # 3. Generar la visualización de red (delegado al servicio)
        fig = generate_keyword_network(abstracts)

        # 4. Renderizar a bytes para streaming (delegado al servicio)
        image_bytes = render_figure_to_bytes(fig)

        # 5. Devolver respuesta streaming
        return StreamingResponse(image_bytes, media_type="image/png")

    except Exception as e:
        # Log the error for debugging
        import logging
        logging.error(f"Error generating keyword network: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating visualization: {str(e)}")


# En main.py - agregar al final antes de la función health_check

@app.get(
    "/stats/terms_by_category",
    summary="Frecuencia de términos por categoría",
    response_description="Análisis de frecuencia de aparición de términos categorizados"
)
def terms_by_category():
    try:
        # Obtener los datos
        json_list = fetch_json_data()

        # Extraer los abstracts
        abstracts = [item.get("abstract", "") for item in json_list]

        # Obtener frecuencias por categoría
        from services.keyword_service import get_terms_frequency_by_category
        results = get_terms_frequency_by_category(abstracts)

        return {"status": "ok", "categories": results}
    except Exception as e:
        import logging
        logging.error(f"Error generando frecuencias por categoría: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analizando términos: {str(e)}")

@app.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}

