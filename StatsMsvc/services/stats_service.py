import pandas as pd
from typing import List, Dict, Any

# Mapeo de tipos de documento a categorías estándar
doc_type_mapping = {
    'Article': 'Artículo',
    'Conference Paper': 'Conferencia',
    'Book Chapter': 'Capítulo de libro',
    'Book': 'Libro',
    'Journal Article': 'Artículo',
    'eBook': 'Libro',
    'Comparative Study': 'Estudio comparativo',
    'Reports - Research': 'Informe de investigación',
}



def _preprocess(json_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Normaliza y extrae campos relevantes de una lista de referencias JSON.
    Incluye manejo robusto de valores nulos y mapeo flexible de tipos y fuentes.
    """
    df = pd.DataFrame(json_list)

    # Parsear lista de autores desde 'contributors'
    def _split_authors(x):
        if isinstance(x, str) and x.strip():
            return [a.strip() for a in x.split(';') if a.strip()]
        return []

    df['authors_list'] = df.get('contributors', '').apply(_split_authors)
    df['first_author'] = df['authors_list'].apply(lambda lst: lst[0] if lst else None)

    # Extraer año desde 'publicationDate'
    def _extract_year(x):
        if isinstance(x, str) and len(x) >= 4 and x[:4].isdigit():
            return int(x[:4])
        return None

    df['year'] = df.get('publicationDate', '').apply(_extract_year)

    # Normalizar tipo de documento desde 'docTypes'
    def _normalize_doc_type(x):
        if isinstance(x, str):
            for key in doc_type_mapping:
                if key.lower() in x.lower():
                    return doc_type_mapping[key]
        return 'Otro'

    df['product_type'] = df.get('docTypes', '').apply(_normalize_doc_type)

    # Usar 'source' como respaldo para 'journal'
    df['journal'] = df.get('journal')
    if df['journal'].isnull().all():
        df['journal'] = df.get('source')

    # Usar 'publisher' o 'publisherLocations' según disponibilidad
    df['publisher'] = df.get('publisher')
    if df['publisher'].isnull().all():
        df['publisher'] = df.get('publisherLocations')

    # Filtrar solo las columnas necesarias
    return df[['first_author', 'year', 'product_type', 'journal', 'publisher']]


def top_first_authors(json_list: List[Dict[str, Any]], top_n: int = 15) -> List[Dict[str, Any]]:
    df = _preprocess(json_list)
    return (
        df['first_author']
          .dropna()
          .value_counts()
          .head(top_n)
          .rename_axis('author')
          .reset_index(name='count')
          .to_dict(orient='records')
    )


def count_by_product_type(json_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    df = _preprocess(json_list)
    return (
        df['product_type']
          .value_counts()
          .rename_axis('type')
          .reset_index(name='count')
          .to_dict(orient='records')
    )


def year_by_product_type(json_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    df = _preprocess(json_list)
    grouped = (
        df.groupby(['year', 'product_type'])
          .size()
          .reset_index(name='count')
          .sort_values(['year', 'count'], ascending=[True, False])
    )
    return grouped.to_dict(orient='records')


def top_journals(json_list: List[Dict[str, Any]], top_n: int = 15) -> List[Dict[str, Any]]:
    df = _preprocess(json_list)
    return (
        df['journal']
          .dropna()
          .value_counts()
          .head(top_n)
          .rename_axis('journal')
          .reset_index(name='count')
          .to_dict(orient='records')
    )


def top_publishers(json_list: List[Dict[str, Any]], top_n: int = 15) -> List[Dict[str, Any]]:
    df = _preprocess(json_list)
    return (
        df['publisher']
          .dropna()
          .value_counts()
          .head(top_n)
          .rename_axis('publisher')
          .reset_index(name='count')
          .to_dict(orient='records')
    )


def generate_all_stats(json_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        'top_authors': top_first_authors(json_list),
        'by_type': count_by_product_type(json_list),
        'year_by_type': year_by_product_type(json_list),
        'top_journals': top_journals(json_list),
        'top_publishers': top_publishers(json_list),
    }
