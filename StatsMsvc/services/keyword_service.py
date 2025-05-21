from typing import List, Dict
from collections import Counter
import itertools
import networkx as nx

CATEGORIES = {
    "Habilidades": [
        "abstraction", "algorithm", "algorithmic thinking", "coding", "collaboration",
        "cooperation", "creativity", "critical thinking", "debug", "decomposition",
        "evaluation", "generalization", "logic", "logical thinking", "modularity",
        "patterns recognition", "problem solving", "programming"
    ],
    "Conceptos Computacionales": [
        "conditionals", "control structures", "directions", "events", "funtions",
        "loops", "modular structure", "parallelism", "sequences", "software/hardware",
        "variables"
    ],
    "Actitudes": [
        "emotional", "engagement", "motivation", "perceptions", "persistence",
        "self-efficacy", "self-perceived"
    ],
    "Propiedades psicométricas": [
        "classical test theory", "confirmatory factor analysis", "exploratory factor analysis",
        "item response theory", "reliability", "structural equation model", "validity"
    ],
    "Herramienta de evaluación": [
        "beginners computational thinking test", "coding attitudes survey",
        "collaborative computing observation instrument", "competent computational thinking test",
        "computational thinking skills test", "computational concepts",
        "computational thinking assessment for chinese elementary students",
        "computational thinking challenge", "computational thinking levels scale",
        "computational thinking scale", "computational thinking skill levels scale",
        "computational thinking test", "computational thinking test for elementary school students",
        "computational thinking test for lower primary",
        "computational thinking-skill tasks on numbers and arithmetic",
        "computerized adaptive programming concepts test", "ct scale",
        "elementary student coding attitudes survey", "general self-efficacy scale",
        "ict competency test", "instrument of computational identity",
        "kbit fluid intelligence subtest",
        "mastery of computational concepts test and an algorithmic test",
        "multidimensional 21st century skills scale", "self-efficacy scale",
        "stem learning attitude scale", "the computational thinking scale"
    ],
    "Diseño de investigación": [
        "no experimental", "experimental", "longitudinal research", "mixed methods",
        "post-test", "pre-test", "quasi-experiments"
    ],
    "Nivel de escolaridad": [
        "upper elementary education", "primary school", "early childhood education",
        "secondary school", "high school", "university"
    ],
    "Medio": [
        "block programming", "mobile application", "pair programming", "plugged activities",
        "programming", "robotics", "spreadsheet", "stem", "unplugged activities"
    ],
    "Estrategia": [
        "construct-by-self mind mapping", "construct-on-scaffold mind mapping",
        "design-based learning", "evidence-centred design approach", "gamification",
        "reverse engineering pedagogy", "technology-enhanced learning", "collaborative learning",
        "cooperative learning", "flipped classroom", "game-based learning", "inquiry-based learning",
        "personalized learning", "problem-based learning", "project-based learning",
        "universal design for learning"
    ],
    "Herramienta": [
        "alice", "arduino", "scratch", "scratchjr", "blockly games", "code.org", "codecombat",
        "csunplugged", "robot turtles", "hello ruby", "kodable", "lightbotjr", "kibo robots",
        "bee bot", "cubetto", "minecraft", "agent sheets", "mimo", "py-learn", "spacechem"
    ]
}



# Lista unificada de términos
terms_list = [
    "abstraction", "algorithm", "algorithmic thinking", "coding", "collaboration",
    "cooperation", "creativity", "critical thinking", "debug", "decomposition",
    "evaluation", "generalization", "logic", "logical thinking", "modularity",
    "patterns recognition", "problem solving", "programming", "conditionals",
    "control structures", "directions", "events", "funtions", "loops",  # "functions" typo
    "modular structure", "parallelism", "sequences", "software/hardware",
    "variables", "emotional", "engagement", "motivation", "perceptions",
    "persistence", "self-efficacy", "self-perceived", "classical test theory",
    "confirmatory factor analysis", "exploratory factor analysis", "item response theory",
    "reliability", "structural equation model", "validity",
    "beginners computational thinking test", "coding attitudes survey",
    "collaborative computing observation instrument", "competent computational thinking test",
    "computational thinking skills test", "computational concepts",
    "computational thinking assessment for chinese elementary students",
    "computational thinking challenge", "computational thinking levels scale",
    "computational thinking scale", "computational thinking skill levels scale",
    "computational thinking test", "computational thinking test for elementary school students",
    "computational thinking test for lower primary",
    "computational thinking-skill tasks on numbers and arithmetic",
    "computerized adaptive programming concepts test", "ct scale",
    "elementary student coding attitudes survey", "general self-efficacy scale",
    "ict competency test", "instrument of computational identity",
    "kbit fluid intelligence subtest",
    "mastery of computational concepts test and an algorithmic test",
    "multidimensional 21st century skills scale", "self-efficacy scale",
    "stem learning attitude scale", "the computational thinking scale",
    "no experimental", "experimental", "longitudinal research", "mixed methods",
    "post-test", "pre-test", "quasi-experiments", "upper elementary education",
    "primary school", "early childhood education", "secondary school", "high school",
    "university", "block programming", "mobile application", "pair programming",
    "plugged activities", "programming", "robotics", "spreadsheet", "stem",
    "unplugged activities", "construct-by-self mind mapping",
    "construct-on-scaffold mind mapping", "design-based learning",
    "evidence-centred design approach", "gamification", "reverse engineering pedagogy",
    "technology-enhanced learning", "collaborative learning", "cooperative learning",
    "flipped classroom", "game-based learning", "inquiry-based learning",
    "personalized learning", "problem-based learning", "project-based learning",
    "universal design for learning", "alice", "arduino", "scratch", "scratchjr",
    "blockly games", "code.org", "codecombat", "csunplugged", "robot turtles",
    "hello ruby", "kodable", "lightbotjr", "kibo robots", "bee bot", "cubetto",
    "minecraft", "agent sheets", "mimo", "py-learn", "learn", "spacechem"
]

# Construir mapeo de sinónimos: forma canónica con key en minúscula y guiones
def build_syn_map(terms: List[str]) -> Dict[str, str]:
    syn_map = {}
    for term in terms:
        key = term.lower().replace(' ', '-')
        syn_map[key] = term
    return syn_map

# Mapa de sinónimos unificado
SYN_MAP = build_syn_map(terms_list)

# Extrae términos presentes en un texto usando el mapa de sinónimos
def extract_terms(text: str, syn_map: Dict[str, str]) -> List[str]:
    found = []
    if not isinstance(text, str):
        return found

    low = text.lower()
    for key, canon in syn_map.items():
        key_words = key.replace('-', ' ')
        if key_words in low or key in low:
            found.append(canon)
    return found

# Frecuencia total de aparición de términos
def frequency(abstracts: List[str]) -> Counter:
    counter = Counter()
    for text in abstracts:
        terms = extract_terms(text, SYN_MAP)
        counter.update(terms)
    return counter

# Grafo de co-ocurrencia
def build_cooccurrence(abstracts: List[str], syn_map: Dict[str, str]) -> nx.Graph:
    g = nx.Graph()
    term_freq = Counter()

    for text in abstracts:
        if isinstance(text, str):
            terms = extract_terms(text, syn_map)
            term_freq.update(terms)

    for term, freq in term_freq.items():
        g.add_node(term, frequency=freq)

    for text in abstracts:
        if not isinstance(text, str):
            continue
        terms = set(extract_terms(text, syn_map))
        for u, v in itertools.combinations(terms, 2):
            if g.has_edge(u, v):
                g[u][v]['weight'] += 1
            else:
                g.add_edge(u, v, weight=1)

    return g


def get_terms_frequency_by_category(abstracts: List[str]) -> Dict[str, Dict[str, int]]:
    """
    Analiza los abstracts y devuelve la frecuencia de aparición de términos por categoría
    """
    # Inicializar resultados con categorías vacías
    results = {category: {} for category in CATEGORIES}

    # Procesar cada abstract
    for abstract in abstracts:
        if not isinstance(abstract, str):
            continue

        # Extraer términos usando la función existente
        terms = extract_terms(abstract, SYN_MAP)

        # Clasificar cada término encontrado en su categoría
        for term in terms:
            for category, cat_terms in CATEGORIES.items():
                if term.lower() in [t.lower() for t in cat_terms]:
                    if term not in results[category]:
                        results[category][term] = 0
                    results[category][term] += 1
                    break

    return results