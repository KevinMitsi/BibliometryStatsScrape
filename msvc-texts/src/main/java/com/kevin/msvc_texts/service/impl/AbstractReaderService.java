package com.kevin.msvc_texts.service.impl;

import com.kevin.msvc_texts.DTO.RefItem;
import com.kevin.msvc_texts.http.FeignScrapper;
import com.kevin.msvc_texts.service.AbstractReader;
import org.springframework.stereotype.Service;
import java.util.*;

import java.util.stream.IntStream;

@Service
public class AbstractReaderService implements AbstractReader {
    private final FeignScrapper feignScrapper;

    // Umbrales de similitud
    private static final double COSINE_THRESHOLD = 0.5;
    private static final double JACCARD_THRESHOLD = 0.3;

    public AbstractReaderService(FeignScrapper feignScrapper) {
        this.feignScrapper = feignScrapper;
    }

    @Override
    public List<String> read() {
        // Obtenemos los datos y eliminamos duplicados exactos
        List<RefItem> uniqueItems = removeDuplicates(feignScrapper.getAllItems().getData());

        return uniqueItems.stream()
                .map(RefItem::getAbstractText)
                .toList();
    }

    public List<String> readTitles(){
        // Obtenemos los datos y eliminamos duplicados exactos
        List<RefItem> uniqueItems = removeDuplicates(feignScrapper.getAllItems().getData());

        return uniqueItems.stream()
                .map(RefItem::getTittleText)
                .toList();
    }

    /**
     * Elimina referencias bibliográficas duplicadas (100% similares)
     * @param items Lista de referencias bibliográficas
     * @return Lista de referencias bibliográficas sin duplicados exactos
     */
    private List<RefItem> removeDuplicates(List<RefItem> items) {
        Set<String> seenItems = new HashSet<>();
        return items.stream()
                .filter(item -> {
                    // Creamos una clave única basada en título y abstract
                    String titleText = item.getTittleText() != null ? item.getTittleText() : "";
                    String abstractText = item.getAbstractText() != null ? item.getAbstractText() : "";
                    String uniqueKey = titleText + "|" + abstractText;

                    // Si la clave ya existe, filtramos este elemento
                    if (seenItems.contains(uniqueKey)) {
                        return false;
                    }

                    // Agregamos la clave y mantenemos el elemento
                    seenItems.add(uniqueKey);
                    return true;
                })
                .toList();
    }

    @Override
    public Map<List<String>, List<String>> getAbstractsSimilar() {
        List<String> abstracts = read();
        List<String> titles = readTitles();

        // Paso 1: Preprocesar datos
        PreprocessedData data = preprocessAbstracts(abstracts);

        // Paso 2: Encontrar pares similares
        List<Set<Integer>> similarGroups = findSimilarGroups(data, abstracts.size());

        // Paso 3: Unir grupos relacionados
        mergeRelatedGroups(similarGroups);

        // Paso 4: Construir el mapa de resultado
        return buildResultMap(similarGroups, titles, abstracts);
    }

    /**
     * Preprocesa los abstracts para calcular tokens, frecuencias y normas.
     */
    private PreprocessedData preprocessAbstracts(List<String> abstracts) {
        int n = abstracts.size();
        List<List<String>> tokens = new ArrayList<>(n);
        List<Map<String, Integer>> freqs = new ArrayList<>(n);
        double[] norms = new double[n];
        List<Set<String>> sets = new ArrayList<>(n);

        for (int i = 0; i < n; i++) {
            List<String> tk = tokenize(abstracts.get(i));
            tokens.add(tk);

            Map<String, Integer> freq = calculateFrequencies(tk);
            freqs.add(freq);

            norms[i] = calculateNorm(freq);
            sets.add(new HashSet<>(tk));
        }

        return new PreprocessedData(tokens, freqs, norms, sets);
    }

    /**
     * Calcula las frecuencias de tokens en una lista.
     */
    private Map<String, Integer> calculateFrequencies(List<String> tokens) {
        Map<String, Integer> freq = new HashMap<>();
        for (String token : tokens) {
            freq.merge(token, 1, Integer::sum);
        }
        return freq;
    }

    /**
     * Calcula la norma de un vector de frecuencias.
     */
    private double calculateNorm(Map<String, Integer> freq) {
        double sumSq = freq.values().stream()
                .mapToDouble(v -> (double) v * v)
                .sum();
        return Math.sqrt(sumSq);
    }

    /**
     * Encuentra grupos de abstracts similares basados en métricas de similitud.
     */
    private List<Set<Integer>> findSimilarGroups(PreprocessedData data, int n) {
        List<Set<Integer>> similarGroups = Collections.synchronizedList(new ArrayList<>());

        IntStream.range(0, n).parallel().forEach(i -> {
            for (int j = i + 1; j < n; j++) {
                if (areSimilar(data, i, j)) {
                    addToSimilarGroups(similarGroups, i, j);
                }
            }
        });

        return similarGroups;
    }

    /**
     * Determina si dos abstracts son similares según umbrales de coseno y Jaccard.
     */
    private boolean areSimilar(PreprocessedData data, int i, int j) {
        double cosSim = computeCosine(
                data.freqs.get(i),
                data.freqs.get(j),
                data.norms[i],
                data.norms[j]
        );

        if (cosSim < COSINE_THRESHOLD) {
            return false;
        }

        double jacSim = computeJaccard(data.sets.get(i), data.sets.get(j));
        return jacSim >= JACCARD_THRESHOLD;
    }

    /**
     * Agrega un par de índices similares a los grupos existentes o crea un nuevo grupo.
     */
    private synchronized void addToSimilarGroups(List<Set<Integer>> similarGroups, int i, int j) {
        // Buscar grupos existentes que contengan i o j
        for (Set<Integer> group : similarGroups) {
            if (group.contains(i) || group.contains(j)) {
                group.add(i);
                group.add(j);
                return;
            }
        }

        // Si no se encontró ninguno, crear un nuevo grupo
        Set<Integer> newGroup = new HashSet<>();
        newGroup.add(i);
        newGroup.add(j);
        similarGroups.add(newGroup);
    }

    /**
     * Une grupos que comparten al menos un elemento en común.
     */
    private void mergeRelatedGroups(List<Set<Integer>> similarGroups) {
        boolean merged;
        do {
            merged = tryMergeGroups(similarGroups);
        } while (merged);
    }

    /**
     * Intenta unir grupos y retorna true si se realizó alguna fusión.
     */
    private boolean tryMergeGroups(List<Set<Integer>> similarGroups) {
        for (int i = 0; i < similarGroups.size(); i++) {
            for (int j = i + 1; j < similarGroups.size(); j++) {
                Set<Integer> intersection = new HashSet<>(similarGroups.get(i));
                intersection.retainAll(similarGroups.get(j));

                if (!intersection.isEmpty()) {
                    similarGroups.get(i).addAll(similarGroups.get(j));
                    similarGroups.remove(j);
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Construye el mapa de resultado final.
     */
    private Map<List<String>, List<String>> buildResultMap(
            List<Set<Integer>> similarGroups,
            List<String> titles,
            List<String> abstracts) {

        Map<List<String>, List<String>> result = new HashMap<>();

        for (Set<Integer> group : similarGroups) {
            List<String> groupTitles = new ArrayList<>();
            List<String> groupAbstracts = new ArrayList<>();

            for (Integer idx : group) {
                groupTitles.add(titles.get(idx));
                groupAbstracts.add(abstracts.get(idx));
            }

            result.put(groupTitles, groupAbstracts);
        }

        return result;
    }

    /**
     * Clase para encapsular los datos preprocesados.
     */
    private record PreprocessedData(List<List<String>> tokens,
                                    List<Map<String, Integer>> freqs,
                                    double[] norms,
                                    List<Set<String>> sets) {
        @Override
        public int hashCode() {
            return Objects.hash(tokens, freqs, Arrays.hashCode(norms), sets);
        }
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof PreprocessedData that)) return false;
            return Arrays.equals(norms, that.norms) && Objects.equals(tokens, that.tokens) && Objects.equals(freqs, that.freqs) && Objects.equals(sets, that.sets);
        }
        @Override
        public String toString() {
            return "PreprocessedData{" +
                    "tokens=" + tokens +
                    ", freqs=" + freqs +
                    ", norms=" + Arrays.toString(norms) +
                    ", sets=" + sets +
                    '}';
        }
    }

    private double computeCosine(Map<String, Integer> f1, Map<String, Integer> f2, double norm1, double norm2) {
        // Iterar sobre la intersección de claves para menor costo
        if (norm1 == 0 || norm2 == 0) return 0.0;
        double dot = 0.0;
        // Elegir la frecuencia más pequeña para iterar
        Map<String, Integer> small = f1.size() < f2.size() ? f1 : f2;
        Map<String, Integer> large = small == f1 ? f2 : f1;
        for (Map.Entry<String, Integer> e : small.entrySet()) {
            Integer v2 = large.get(e.getKey());
            if (v2 != null) dot += e.getValue() * v2;
        }
        return dot / (norm1 * norm2);
    }

    private double computeJaccard(Set<String> s1, Set<String> s2) {
        if (s1.isEmpty() || s2.isEmpty()) return 0.0;
        Set<String> inter = new HashSet<>(s1);
        inter.retainAll(s2);
        int sizeInter = inter.size();

        // s1 + s2 - inter
        int sizeUnion = s1.size() + s2.size() - sizeInter;
        return (double) sizeInter / sizeUnion;
    }

    private List<String> tokenize(String text) {
        if (text == null || text.isBlank()) {
            return Collections.emptyList();
        }
        return Arrays.stream(text
                        .toLowerCase(Locale.ROOT)
                        .replaceAll("[^a-z0-9 ]", " ")
                        .split("\\s+"))
                .filter(t -> !t.isBlank())
                .toList();
    }
}