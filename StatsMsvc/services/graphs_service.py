import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict, Any

from services.stats_service import (
    top_first_authors,
    count_by_product_type,
    year_by_product_type,
    top_journals,
    top_publishers
)


def generate_stats_plot(json_list: List[Dict[str, Any]]) -> plt.Figure:
    data = count_by_product_type(json_list)
    df = pd.DataFrame(data)
    df['type'] = df['type'].apply(lambda x: x if isinstance(x, str) else str(x))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df['type'], df['count'])
    ax.set_xticks(range(len(df['type'])))
    ax.set_xticklabels(df['type'], rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title('Publications by Product Type')
    fig.tight_layout()
    return fig


def generate_authors_plot(json_list: List[Dict[str, Any]]) -> plt.Figure:
    data = top_first_authors(json_list)
    df = pd.DataFrame(data)
    df['author'] = df['author'].apply(lambda x: x if isinstance(x, str) else str(x))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df['author'], df['count'])
    ax.set_xticks(range(len(df['author'])))
    ax.set_xticklabels(df['author'], rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title('Top First Authors')
    fig.tight_layout()
    return fig


def generate_year_by_type_plot(json_list: List[Dict[str, Any]]) -> plt.Figure:
    data = year_by_product_type(json_list)
    df = pd.DataFrame(data)
    df['product_type'] = df['product_type'].apply(lambda x: x if isinstance(x, str) else str(x))

    pivot = df.pivot(index='year', columns='product_type', values='count').fillna(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    for col in pivot.columns:
        ax.plot(pivot.index, pivot[col], label=col)
    ax.set_xlabel('Year')
    ax.set_ylabel('Count')
    ax.set_title('Publications by Year and Type')
    ax.legend()
    fig.tight_layout()
    return fig

def generate_journals_plot(json_list: List[Dict[str, Any]]) -> plt.Figure:
    def shorten_name(name: str, max_length: int = 30) -> str:
        return name if len(name) <= max_length else name[:max_length - 3] + '...'

    data = top_journals(json_list)
    df = pd.DataFrame(data)
    df['journal'] = df['journal'].apply(lambda x: x if isinstance(x, str) else str(x))
    df['short_journal'] = df['journal'].apply(lambda x: shorten_name(x, max_length=20))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(df['short_journal'], df['count'])
    ax.set_xticks(range(len(df['short_journal'])))
    ax.set_xticklabels(df['short_journal'], rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title('Top Journals')
    fig.tight_layout()
    return fig



def generate_publishers_plot(json_list: List[Dict[str, Any]]) -> plt.Figure:
    data = top_publishers(json_list)
    df = pd.DataFrame(data)
    df['publisher'] = df['publisher'].apply(lambda x: x if isinstance(x, str) else str(x))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df['publisher'], df['count'])
    ax.set_xticks(range(len(df['publisher'])))
    ax.set_xticklabels(df['publisher'], rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title('Top Publishers')
    # Ajustar límite y-axis para incluir todos los valores
    max_count = df['count'].max()
    ax.set_ylim(0, max_count * 1.1)
    fig.tight_layout()
    return fig