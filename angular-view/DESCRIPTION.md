# Bibliometry View - Documentación de Servicios y Componentes

## Índice
1. Servicios
   - ScrapperService
   - StatsService
   - TextsService
2. Componentes
   - AppComponent
   - Requerimiento1Component
   - Requerimiento2Component
   - Requerimiento3Component
   - Requerimiento4Component
   - StatsCardComponent

## Servicios

### ScrapperService

**Ubicación**: `src/app/services/scrapper-service.service.ts`

**Descripción**: Este servicio gestiona las peticiones al backend para realizar scraping de datos bibliométricos.

**Funcionalidades principales**:
- `postScrape()`: Realiza una petición para buscar y extraer artículos científicos usando credenciales, texto de búsqueda y límite de resultados.
- `getRepeated()`: Obtiene información sobre artículos duplicados que han sido eliminados del conjunto de datos.

### StatsService

**Ubicación**: `src/app/services/stats-service.service.ts`

**Descripción**: Gestiona la obtención de estadísticas y gráficos basados en los datos bibliométricos recopilados.

**Funcionalidades principales**:
- **Endpoints de JSON**:
  - `getAuthors()`: Obtiene datos sobre los autores más frecuentes.
  - `getTypes()`: Obtiene estadísticas por tipo de documento.
  - `getYearByType()`: Obtiene distribución de documentos por año y tipo.
  - `getJournals()`: Obtiene las revistas más frecuentes.
  - `getPublishers()`: Obtiene las editoriales más frecuentes.
  - `getTermsByCategory()`: Obtiene términos organizados por categorías.

- **Endpoints de gráficos**:
  - `getAuthorsPlot()`: Obtiene visualización de autores en formato Blob (imagen).
  - `getTypesPlot()`: Obtiene visualización de tipos en formato Blob.
  - `getYearByTypePlot()`: Obtiene visualización de año por tipo en formato Blob.
  - `getJournalsPlot()`: Obtiene visualización de revistas en formato Blob.
  - `getPublishersPlot()`: Obtiene visualización de editoriales en formato Blob.
  
- **Visualizaciones especiales**:
  - `getCooccurrencePlot()`: Obtiene grafo de co-ocurrencia de palabras clave.
  - `getWordcloudPlot()`: Obtiene nube de palabras.

### TextsService

**Ubicación**: `src/app/services/texts-service.service.ts`

**Descripción**: Maneja el análisis de texto y algoritmos de similitud para agrupar documentos similares.

**Funcionalidades principales**:
- `getKeywordClusters()`: Obtiene clusters de artículos agrupados por similitud de texto entre títulos y resúmenes.

## Componentes

### AppComponent

**Ubicación**: `src/app/app.component.ts`

**Descripción**: Componente raíz de la aplicación.

**Funcionalidades**:
- Define la estructura principal con cabecera, navegación y contenido.
- Gestiona la navegación entre los diferentes requerimientos mediante router-outlet.

**Interfaz**:
- Barra de navegación con enlaces a los cuatro requerimientos principales.
- Título de la aplicación.
- Contenedor principal donde se cargan los demás componentes.

### Requerimiento1Component

**Ubicación**: `src/app/components/requerimiento1/requerimiento1.component.ts`

**Descripción**: Componente para la extracción inicial de datos (scraping).

**Funcionalidades principales**:
- Formulario para ingresar criterios de búsqueda (texto, email, contraseña y número de resultados).
- Validación de formulario.
- Visualización de resultados en tabla.
- Listado de artículos duplicados eliminados.

**Interfaces definidas**:
- `Article`: Define la estructura de un artículo con campos como título, autores, DOI, etc.
- `ScrapeResponse`: Respuesta del servicio de scrape.
- `RepeatedArticle`: Estructura para artículos duplicados.
- `RepeatedArticleResponse`: Respuesta del servicio de artículos duplicados.

### Requerimiento2Component

**Ubicación**: `src/app/components/requerimiento2/requerimiento2.component.ts`

**Descripción**: Muestra estadísticas y visualizaciones de los datos bibliométricos.

**Funcionalidades principales**:
- Inicializa y configura múltiples tarjetas de estadísticas.
- Cada tarjeta muestra estadísticas sobre una categoría específica (autores, tipos, años, revistas, editoriales).
- Permite cargar datos JSON y visualizaciones para cada categoría.

**Características**:
- Utiliza componentes `StatsCardComponent` reutilizables para cada tipo de estadística.
- Sanitiza URLs de recursos para visualizaciones seguras.
- Maneja errores en carga de datos y visualizaciones.

### Requerimiento3Component

**Ubicación**: `src/app/components/requerimiento3/requerimiento3.component.ts`

**Descripción**: Muestra análisis de co-ocurrencia de términos y nubes de palabras.

**Funcionalidades principales**:
- `loadCooccurrence()`: Carga y muestra el grafo de co-ocurrencia de términos.
- `loadWordcloud()`: Carga y muestra la nube de palabras.
- `loadTermsByCategory()`: Carga y muestra términos organizados por categorías.

**Interfaces definidas**:
- `TermsByCategoryResponse`: Estructura de respuesta para términos por categoría.
- `CategoryTerm`: Estructura de un término asociado a una categoría.

### Requerimiento4Component

**Ubicación**: `src/app/components/requerimiento4/requerimiento4.component.ts`

**Descripción**: Implementa algoritmos de similitud de texto para agrupar artículos similares.

**Funcionalidades principales**:
- `loadClusters()`: Carga clusters de artículos agrupados por similitud.
- `setView()`: Cambia entre vista de solo títulos y vista completa (títulos + abstracts).

**Interfaces definidas**:
- `Cluster`: Define un grupo de títulos y abstracts relacionados.

**Características**:
- Visualización tabular de clusters.
- Opción para ver solo títulos o títulos con abstracts.
- Manejo de estados de carga y errores.

### StatsCardComponent

**Ubicación**: `src/app/components/stats-card/stats-card.component.ts`

**Descripción**: Componente reutilizable para mostrar estadísticas y visualizaciones.

**Funcionalidades principales**:
- `onLoadJson()`: Carga datos estadísticos en formato JSON.
- `onLoadPlot()`: Carga visualizaciones (gráficos).

**Propiedades**:
- `@Input() config`: Configuración de la tarjeta (título, funciones de carga, estados).

**Características**:
- Reutilizable para diferentes tipos de estadísticas.
- Manejo de estados de carga.
- Gestión de errores en la carga de datos y visualizaciones.
- Visualización de datos JSON y gráficos.