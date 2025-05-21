from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json

from fastapi.middleware.cors import CORSMiddleware

from src.services import scrapper_service
from src.services.conversor import XmlToJsonConverter


# Define request schema
class ScrapeRequest(BaseModel):
    search_string: str
    email: str
    password: str
    top_results: int

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200",       # Para desarrollo local en su máquina
        "http://bibliometry-view:80",         # Para solicitudes desde el contenedor Angular (si ese es su nombre)
        "http://bibliometry-view",            # Variante sin puerto
        "http://bibliometry-view:4200",       # Si mapea al puerto 4200 dentro del contenedor
        "http://172.17.0.1:4200",  ],  # Reemplaza con la URL de tu frontend Angular
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
# Endpoint to trigger scraping and conversion
@app.post("/scrape")
def scrape_and_convert(request: ScrapeRequest):
    """
    Executes the scraper service and then converts downloaded XML files to JSON.
    Returns the cleaned JSON data.
    """
    try:
        # Run the scraper (blocking call)
        scrapper_service.main(
            search_string=request.search_string,
            mail=request.email,
            key=request.password,
            top_results=request.top_results
        )

        # After scraping completes, convert XMLs to JSON list
        download_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src/refs"))
        converter = XmlToJsonConverter(xml_dir=download_dir)
        json_data = converter.convert_xmls_to_list()

        return {"status": "success", "data": json_data}

    except Exception as e:
        # Return error response if anything goes wrong
        raise HTTPException(status_code=500, detail=str(e))

# Optional endpoint: convert existing XMLs without scraping
@app.get("/convert")
def convert_existing():
    """
    Converts any XML files already present in the refs directory to JSON.
    """
    try:
        download_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src/refs"))
        converter = XmlToJsonConverter(xml_dir=download_dir)
        json_data = converter.convert_xmls_to_list()

        return {"status": "converted", "data": json_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repeated")
def get_repeated_files():
    """Devuelve el contenido del archivo repeated.json"""
    try:
        repeated_json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src/repeated.json"))

        if not os.path.exists(repeated_json_path):
            return {"status": "success", "data": [], "message": "No se han detectado registros repetidos"}

        with open(repeated_json_path, 'r', encoding='utf-8') as f:
            repeated_data = json.load(f)

        return {"status": "success", "data": repeated_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo de repetidos: {str(e)}")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
