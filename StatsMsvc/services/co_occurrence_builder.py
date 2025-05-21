import io
from collections import Counter
from typing import List, Dict, Tuple

import community.community_louvain as cl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.cm import get_cmap
from matplotlib.colors import to_hex

from services.keyword_service import SYN_MAP, build_cooccurrence, extract_terms


def generate_keyword_network(abstracts: List[str]) -> plt.Figure:
    # Construye el grafo de co-ocurrencia usando el mapa unificado
    g = build_cooccurrence(abstracts, SYN_MAP)
    assert isinstance(g, nx.Graph), f"g debe ser nx.Graph, pero es {type(g)}"

    # Si no hay nodos, devolvemos figura vacía con mensaje
    if g.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.text(0.5, 0.5, "No keywords found in abstracts",
                ha='center', va='center', fontsize=16)
        ax.axis('off')
        return fig

    # Recalcula frecuencias totales para filtrado
    term_freq: Counter = Counter()
    for txt in abstracts:
        if isinstance(txt, str):
            term_freq.update(extract_terms(txt, SYN_MAP))

    # Filtrar nodos con frecuencia < 2
    g = g.subgraph([n for n in g.nodes() if term_freq.get(n, 0) >= 2]).copy()
    assert isinstance(g, nx.Graph), f"Tras subgraph, g debe ser nx.Graph, pero es {type(g)}"

    # Quitar edges con peso < 2 y nodos aislados
    to_remove = [(u, v) for u, v, d in g.edges(data=True)
                 if float(d.get('weight', 1)) < 2]
    g.remove_edges_from(to_remove)
    g.remove_nodes_from(list(nx.isolates(g)))
    assert isinstance(g, nx.Graph), f"Tras limpieza, g debe ser nx.Graph, pero es {type(g)}"

    if g.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.text(0.5, 0.5, "No significant keyword co-occurrences found",
                ha='center', va='center', fontsize=16)
        ax.axis('off')
        return fig

    # Detección de comunidades
    partition: Dict[str, int] = cl.best_partition(g)

    # Layout
    try:
        pos: Dict[str, Tuple[float, float]] = nx.kamada_kawai_layout(g)
    except ImportError:
        pos = nx.spring_layout(g, seed=42)
    assert isinstance(pos, dict), f"pos debe ser dict, pero es {type(pos)}"

    fig, ax = plt.subplots(figsize=(16, 12))

    # Dibujar aristas
    weights = nx.get_edge_attributes(g, 'weight')
    max_w = max(weights.values(), default=1.0)
    for (u, v), w in weights.items():
        width = 0.5 + 1.5 * (w / max_w)
        nx.draw_networkx_edges(
            g, pos, edgelist=[(u, v)], width=width,
            edge_color='lightgray', alpha=0.6, ax=ax
        )

    # Dibujar nodos
    max_f = max(term_freq.values(), default=1)
    cmap = get_cmap('tab20b')
    max_cid = max(partition.values())
    norm_factor = max_cid if max_cid > 0 else 1

    for n in g.nodes():
        freq = term_freq.get(n, 0)
        size = 100 + 300 * (freq / max_f)
        cid = partition[n]
        rgba = cmap(cid / norm_factor)
        color = (float(rgba[0]), float(rgba[1]), float(rgba[2]))
        nx.draw_networkx_nodes(
            g, pos, nodelist=[n], node_size=size,
            node_color=to_hex(color), alpha=0.8,
            edgecolors='white', linewidths=0.5, ax=ax
        )

    # Etiquetas para nodos con frecuencia alta
    threshold = 1
    labels = {n: n for n in g.nodes() if term_freq.get(n, 0) >= threshold}
    nx.draw_networkx_labels(g, pos, labels=labels,
                            font_size=10, font_weight='bold', ax=ax)

    # Leyenda de clusters
    legend_handles = []
    for cid in sorted(set(partition.values())):
        nodes = [n for n, c in partition.items() if c == cid]
        rep = max(nodes, key=lambda x: term_freq[x]) if nodes else "N/A"
        rgba = cmap(cid / norm_factor)
        color: Tuple[float, float, float] = (float(rgba[0]), float(rgba[1]), float(rgba[2]))
        legend_handles.append(
            mpatches.Patch(color=color, label=f"Cluster {cid + 1}: {rep}")
        )

    ax.legend(handles=legend_handles, title="Clusters",
              loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_title("Keyword Co-occurrence Network Analysis",
                 fontsize=18, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    return fig


def render_figure_to_bytes(fig: plt.Figure) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf
