# msvc-texts Microservice Documentation

## Overview

`msvc-texts` is a Spring Boot microservice that processes and analyzes text abstracts from reference items. It provides functionality to:
* Retrieve abstracts and titles from a scrapper service
* Remove exact duplicates from the data
* Identify similar abstracts using text similarity algorithms (cosine similarity and Jaccard index)
* Group similar abstracts together for analysis

## Architecture

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

## Endpoints

The service exposes the following REST endpoints:

### GET /texts/health
Health check endpoint.

**Response:** `"Running"` with 200 OK status

### GET /texts/read
Retrieves all abstracts from the source.

**Response:** List of abstract texts

### GET /texts/findSimilar
Finds and groups similar abstracts.

**Response:** A map where:
* Keys: Lists of titles for similar documents
* Values: Lists of corresponding abstracts

## Services

### AbstractReader Interface

```java
public interface AbstractReader {
    List<String> read();
    Map<List<String>, List<String>> getAbstractsSimilar();
}
```

### AbstractReaderService Implementation

This service implements the core functionality of the microservice:

#### Key Methods:

1. **read()** - Retrieves abstracts from the data source
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

2. **readTitles()** - Retrieves titles from the data source
```java
public List<String> readTitles(){
    // Obtenemos los datos y eliminamos duplicados exactos
    List<RefItem> uniqueItems = removeDuplicates(feignScrapper.getAllItems().getData());
    return uniqueItems.stream()
            .map(RefItem::getTittleText)
            .toList();
}
```

3. **getAbstractsSimilar()** - Finds and groups similar abstracts using a text similarity algorithm
```java
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
```

### Similarity Algorithms

The service uses two similarity measures with configurable thresholds:

```java
// Umbrales de similitud
private static final double COSINE_THRESHOLD = 0.5;
private static final double JACCARD_THRESHOLD = 0.3;
```

1. **Cosine Similarity** - Measures the cosine of the angle between vectors of word frequencies
```java
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
```

2. **Jaccard Similarity** - Measures similarity between finite sets
```java
private double computeJaccard(Set<String> s1, Set<String> s2) {
    if (s1.isEmpty() || s2.isEmpty()) return 0.0;
    Set<String> inter = new HashSet<>(s1);
    inter.retainAll(s2);
    int sizeInter = inter.size();
    // s1 + s2 - inter
    int sizeUnion = s1.size() + s2.size() - sizeInter;
    return (double) sizeInter / sizeUnion;
}
```

## Data Transfer Objects (DTOs)

### RefItem

Represents a reference item with title and abstract:

```java
public class RefItem {
    @JsonProperty("title")
    private JsonNode title;
    @JsonProperty("abstract")
    private JsonNode abstractField;
    
    // Methods to access text content safely
    public String getAbstractText() {
        if (abstractField == null || abstractField.isNull()) {
            return null;
        }
        if (abstractField.isTextual()) {
            return abstractField.asText();
        }
        // para objetos/arrays: serializa como JSON
        return abstractField.toString();
    }
    public String getTittleText() {
        if (title == null || title.isNull()) {
            return null;
        }
        if (title.isTextual()) {
            return title.asText();
        }
        // para objetos/arrays: serializa como JSON
        return title.toString();
    }
    
    // Other methods...
}
```

### RefItemResponse

Wrapper for API responses:

```java
public class RefItemResponse {
    @JsonProperty("status")
    private String status;
    @JsonProperty("data")
    private List<RefItem> data;
    
    // Constructors, getters, setters...
}
```

## HTTP Clients

### FeignScrapper

Interface for communicating with the scrapper service:

```java
@FeignClient(name = "scrapper", url = "host.docker.internal:8000")
public interface FeignScrapper {
    @GetMapping("/convert")
    RefItemResponse getAllItems();
}
```

## Configuration

### Application Properties

```properties
spring.application.name=msvc-texts
server.port=8003
```

### Docker Configuration

The service is containerized using a multi-stage Docker build:

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

## Building and Running

### Prerequisites
* Java 17
* Maven 3.8+
* Docker (optional, for containerization)

### Building with Maven
```bash
./mvnw clean package
```

### Running the Application
```bash
java -jar target/msvc-texts-0.0.1-SNAPSHOT.jar
```

### Building and Running with Docker
```bash
# Build the Docker image
docker build -t msvc-texts:latest .

# Run the container
docker run -p 8003:8003 msvc-texts:latest
```

## Integration with Other Services

This microservice is designed to work with:
1. A scrapper service (expected at host.docker.internal:8000)
2. A frontend application (allowed from various origins in CORS configuration)

The service retrieves data from the scrapper service via the `/convert` endpoint and processes it for text similarity analysis.