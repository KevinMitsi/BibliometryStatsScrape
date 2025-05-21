import re
from collections import Counter
from typing import List, Dict, Tuple

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from services.keyword_service import SYN_MAP, extract_terms


def count_keyword_frequencies(
    abstracts: List[str],
    category_variables: Dict[str, List[str]]
) -> Tuple[Dict[str, Counter], Counter]:
    """
    Cuenta la frecuencia de aparición de variables (y sus sinónimos) en los abstracts,
    desglosado por categoría y un conteo total.
    (No usado para la nube general, que usa extract_terms directamente.)
    """
    # Preprocesar category_variables: expandir sinónimos unidos por guion
    expanded_map: Dict[str, List[str]] = {}
    for category, vars_list in category_variables.items():
        expanded = []
        for var in vars_list:
            parts = [v.strip().lower() for v in var.split('-') if v.strip()]
            expanded.extend(parts)
        expanded_map[category] = expanded

    category_counters: Dict[str, Counter] = {cat: Counter() for cat in expanded_map}
    total_counter: Counter = Counter()

    for text in abstracts:
        if not isinstance(text, str):
            continue
        text_lower = text.lower()
        for category, terms in expanded_map.items():
            for term in terms:
                pattern = rf"\b{re.escape(term)}\b"
                count = len(re.findall(pattern, text_lower))
                if count:
                    category_counters[category][term] += count
                    total_counter[term] += count
    return category_counters, total_counter


def generate_wordcloud_from_frequencies(
    frequencies: Counter,
    width: int = 800,
    height: int = 400
) -> plt.Figure:
    if not frequencies:
        fig, ax = plt.subplots(figsize=(width / 100, height / 100))
        ax.text(0.5, 0.5, "No terms to display",
                ha='center', va='center', fontsize=14)
        ax.axis('off')
        return fig

    wc = WordCloud(
        width=width,
        height=height,
        background_color='white',
        collocations=False
    )
    wc.generate_from_frequencies(frequencies)

    fig, ax = plt.subplots(figsize=(width / 100, height / 100))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout()
    return fig


def generate_overall_wordcloud(
    abstracts: List[str]
) -> plt.Figure:
    """
    Genera una nube de palabras combinada para todos los términos extraídos.
    Usa extract_terms con SYN_MAP para normalizar y unir sinónimos.
    """
    total_counter: Counter = Counter()
    for text in abstracts:
        if isinstance(text, str):
            terms = extract_terms(text, SYN_MAP)
            total_counter.update(terms)
    return generate_wordcloud_from_frequencies(total_counter)


def generate_category_wordclouds(
    abstracts: List[str],
    category_variables: Dict[str, List[str]]
) -> Dict[str, plt.Figure]:
    category_counters, _ = count_keyword_frequencies(abstracts, category_variables)
    wordclouds: Dict[str, plt.Figure] = {}
    for category, freqs in category_counters.items():
        wordclouds[category] = generate_wordcloud_from_frequencies(freqs)
    return wordclouds
