# Pipeline NLP: Clustering y Resumen de Noticias con OpenAI

## Contexto del Proyecto

Desarrollo de un pipeline en Python que procesa noticias en JSON, identifica temas comunes y genera resúmenes consolidados por grupo temático, usando la API de OpenAI.

**Formato de entrada:** `[{"id": "str", "title": "str", "body": "str"}, ...]`

---

## Arquitectura General (3 Fases)

1. **Enriquecimiento**: extraer representación semántica de cada noticia (keywords y/o embeddings)
2. **Agrupamiento (Clustering)**: agrupar noticias similares según esa representación
3. **Consolidación**: para los grupos más grandes, generar un resumen único vía LLM

---

## Versión 1: Clustering por Keywords (baseline)

**Técnica:** Extracción de keywords vía prompt a GPT + similitud de Jaccard (intersección/unión de conjuntos de términos) + búsqueda de componentes conexas (DFS) sobre un grafo de similitud.

**Ventajas:**
- Simple, barato, rápido de implementar
- Interpretable (se ve qué términos comparten)

**Limitaciones detectadas:**
- No detecta sinónimos ni relaciones semánticas ("banco central" vs "autoridad monetaria" no matchean)
- Sensible a la variabilidad del vocabulario usado en cada artículo
- Requiere que el LLM extraiga *exactamente* los mismos términos entre artículos relacionados

---

## Versión 2: Clustering con Embeddings (mejora propuesta)

**Problema que resuelve:** capturar similitud *semántica* real, no solo léxica.

**Técnica central:**
- Generar embeddings del texto combinado (título + cuerpo) con `text-embedding-3-large` (API de OpenAI, 3072 dimensiones)
- Calcular similitud coseno entre vectores
- Aplicar un algoritmo de clustering sobre la matriz de embeddings

**Tres métodos de clustering evaluados:**

| Método | Cuándo usarlo | Característica clave |
|---|---|---|
| `AgglomerativeClustering` (jerárquico) | Datasets medianos, resultados estables | `distance_threshold = 1 - similarity_threshold`, `metric='cosine'`, `linkage='average'` |
| `DBSCAN` (basado en densidad) | Hay ruido / outliers (noticias sin tema relacionado) | No requiere definir n° de clusters; label `-1` = outlier |
| **Híbrido (recomendado)** | Datasets heterogéneos, grupos grandes que conviene subdividir | DBSCAN primero → si un cluster tiene >10 items, se subdivide con jerárquico |

**Enfoque híbrido embeddings + keywords (score combinado):**
```
similitud_final = 0.8 * similitud_embeddings + 0.2 * similitud_keywords (Jaccard)
```
- Combina precisión semántica (embeddings) con anclaje explícito en términos (keywords) como señal secundaria/boost.

**Métricas de calidad añadidas por grupo:**
- `avg_similarity`: cohesión interna del cluster (promedio de similitud coseno entre pares dentro del grupo)
- `representative_keywords`: términos más frecuentes del grupo, útiles para etiquetar/inspeccionar el cluster

---

## Comparativa Keywords vs Embeddings

| Aspecto | Keywords (Jaccard) | Embeddings (coseno) |
|---|---|---|
| Tipo de similitud | Léxica/exacta | Semántica |
| Detecta sinónimos/parafraseo | No | Sí |
| Captura contexto | No | Sí |
| Costo computacional | Bajo | Medio (llamadas a API de embeddings) |
| Precisión estimada | ~60-70% | ~85-95% |
| Costo económico | Ninguno extra | `text-embedding-3-large`: ~$0.13 / 1M tokens |

**Recomendación general:** usar embeddings como base y keywords como boost/interpretabilidad, salvo restricciones fuertes de costo o volumen muy alto de datos.

---

## Requisitos Técnicos Cubiertos

- **Asincronía:** `AsyncOpenAI` + `asyncio.gather()` para paralelizar llamadas (extracción de keywords, embeddings, y consolidación final)
- **Control de concurrencia:** `asyncio.Semaphore` para no saturar rate limits
- **Resiliencia:** retry con backoff exponencial (delay que se duplica en cada intento, máx. 3 intentos)
- **Modularidad:** clase `pipeline` con métodos separados por fase (`phase1_...`, `phase2_...`, `phase3_...`), fácil de testear o sustituir por partes

---

## Parámetros Configurables Clave

```python
similarity_threshold   # umbral de similitud (Jaccard o coseno según versión)
top_groups             # cuántos grupos consolidar en resumen final
clustering_method      # "hierarchical" | "dbscan" | "hybrid"
use_keywords           # activar/desactivar boost de keywords
max_concurrent         # límite de requests paralelos
embedding_model        # ej. "text-embedding-3-large"
```

---

## Configuraciones Recomendadas por Escenario

**Noticias generales / volumen moderado:**
```python
clustering_method="hybrid"
similarity_threshold=0.75
use_keywords=True
```

**Datasets muy grandes (>1000 noticias) / prioridad en velocidad y costo:**
```python
clustering_method="dbscan"
similarity_threshold=0.70
use_keywords=False  # solo embeddings, sin llamadas extra a keywords
```

---

## Posibles Mejoras Futuras (no implementadas aún, sugeridas)

1. **Validación de calidad del clustering:**
   - Visualización con t-SNE o UMAP para inspeccionar clusters en 2D
   - Silhouette score para medir objetivamente la separación/cohesión de los clusters y ayudar a elegir `similarity_threshold`

2. **Optimización de costos:**
   - Cachear embeddings si el mismo dataset se reprocesa
   - Usar `text-embedding-3-small` como alternativa más barata si la precisión de `-large` no es crítica

3. **Escalabilidad:**
   - Para datasets muy grandes, considerar índices de vecinos aproximados (ej. FAISS, HNSW) en vez de similitud coseno por fuerza bruta (O(n²))

4. **Calidad del resumen final:**
   - Ajustar longitud/tono del prompt de consolidación según medio de publicación
   - Detectar y filtrar duplicados casi-exactos antes de consolidar (evitar redundancia dentro del mismo grupo)

---

## Estado Actual

Existen dos versiones completas de código Python, funcionales y documentadas:
1. **Baseline:** clustering por keywords + Jaccard + DFS
2. **Mejorada:** clustering por embeddings (jerárquico/DBSCAN/híbrido) + boost de keywords opcional + métricas de cohesión

Ambas comparten la misma estructura de 3 fases y los mismos requisitos de asincronía/resiliencia. La versión mejorada es la recomendada como punto de partida para producción.
