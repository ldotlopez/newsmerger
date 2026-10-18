# newsmerger: definición técnica

Versión consolidada · 18 de octubre de 2026

## 1. Propósito y alcance

newsmerger es un pipeline de **adquisición, enriquecimiento y remezcla** de contenidos, pensado para noticias y con vocación de recolector personal de información genérica. Las herramientas externas que consumen sus resultados quedan fuera del proyecto y acceden a él únicamente mediante la clase `Application`.

Los pipelines (cadenas de procesadores sobre un item) son una funcionalidad externa y en desarrollo: de momento se implementan como scripts externos sobre `Application` y no forman parte de esta definición.

## 2. Glosario

| Término | Definición |
| --- | --- |
| **Fuente (source)** | Entrada de la sección `sources` de la configuración, con `id`, `name`, `provider` y `url`. Su identidad es el `id`. |
| **Origen (provider)** | Plugin que sabe tratar un tipo de sitio. Una misma implementación sirve a todas las URLs con la misma estructura. |
| **Item** | Unidad de contenido adquirida. Clave: `(source id, uid)`. Su `uri` es un dato más, no es única. |
| **uid** | Identificador del item dentro de su fuente, generado por el origen. Debe ser determinista y estable entre ejecuciones; cómo se calcula es decisión del origen. |
| **Anotación** | Dato derivado de un item, producido por un procesador. Clave: `(item, procesador, key)`; un procesador puede emitir varias claves por item. |
| **Remezclador (remixer)** | Plugin que genera artefactos a partir de muchos items. |
| **Artefacto** | Salida agregada de un remezclador (newsletter, RSS, web...). Clave: `(remezclador, nombre)`. |

## 3. Configuración

Un único YAML con las secciones `sources`, `processors`, `remixers`, `cache` y `db`. Todas son opcionales. Cada fuente asigna explícitamente su origen:

```yaml
sources:
  - id: <stable id>        # obligatorio
    name: <readable name>
    provider: <provider plugin>
    url: <url>
processors:
  - name: <processor plugin>
    params: {...}          # se pasan al procesador; incluye max_retries
remixers: ...
cache:
  expiration: <seconds>    # vida de la caché HTTP
db:
  uri: <sqlalchemy uri>    # por defecto, <user data dir>/newsmerger/data.db
  content_dir: <path>      # por defecto, <user data dir>/newsmerger/content
```

Los valores `${VAR}` se sustituyen por variables de entorno al cargar; los secretos (API keys, tokens) se pasan siempre así.

Los plugins de los tres tipos (origen, procesador y remezclador) los carga `foundation.plugin.ClassLoader`. El `id` de una fuente forma parte de la clave de sus items, así que debe ser estable; su `url` y su `provider` pueden cambiar sin perder los items.

## 4. Fases

### 4.1 Importación

Cada fuente se consulta mediante el plugin de su origen, que lista las noticias, extrae el contenido y crea o actualiza un item por noticia.

- **Fechas:** cada item guarda `published_at` y `modified_at`.
  - Item nuevo: ambas vienen del origen; la que falte toma el momento actual.
  - Item cambiado: `modified_at` toma el valor del origen si es más reciente que el almacenado (nunca retrocede); si el origen no lo emite, toma el momento actual. `published_at` se rellena una vez y no se sobrescribe.
- **Detección de cambios:** el item se considera cambiado si difiere alguno de `title`, `uri`, `mimetype`, contenido (`content_sha256`) o `data`. Las fechas no intervienen. Reimportar un item idéntico no escribe nada.
- **Item cambiado:** se sobrescribe. Sus anotaciones se conservan, pero si cambió el contenido, todos sus estados de procesado vuelven a ser elegibles con los intentos a cero. Los artefactos no se invalidan.
- **Duplicados:** una misma noticia en dos fuentes son dos items, incluso si ambas son del mismo origen. La deduplicación, si se desea, es responsabilidad de los remezcladores.
- **Importación de una URL suelta:** debe indicar una fuente configurada, cuyo origen se usa.
- **Fuente eliminada del YAML:** sus items se conservan y dejan de actualizarse. Siguen siendo visibles para los remezcladores.

### 4.2 Enriquecimiento

Los procesadores crean anotaciones sobre los items.

- **Dependencias:** un procesador declara el procesador del que depende. Solo recoge los items que ese procesador terminó con éxito sobre el contenido actual; los demás esperan sin gastar intentos, también con regeneración forzada. Si el procesador del que depende terminó pero falta la anotación que se necesita, el resultado es un fallo reintentable.
- **Resultados posibles:**
  - **Éxito:** se guardan las anotaciones.
  - **Descarte:** el item no aplica a este procesador. Es permanente para ese contenido: solo se reevalúa si el contenido del item cambia o se fuerza la regeneración.
  - **Fallo reintentable:** sin anotaciones.
  - **Fallo parcial:** se guardan las claves obtenidas y el item cuenta como fallo reintentable.
- **Reintentos:** máximo de 3 intentos por defecto, configurable con `max_retries`. Entre intentos hay una espera exponencial de `60 s · 2^(n-1)`, con un máximo de 24 h.
- **Contador de intentos:** vuelve a cero cuando el resultado es éxito o descarte, cuando cambia el contenido del item, al borrar sus anotaciones y al forzar la regeneración desde `Application`.
- **Cardinalidad:** una anotación por `(item, procesador, key)`; regenerar sobrescribe las claves emitidas.
- **Versión del procesador:** cada procesador puede declarar una versión en su código. Al cambiarla, los items que tenía terminados con éxito vuelven a procesarse sin forzar; los descartados y los fallos agotados no.
- Un cambio en la configuración de un procesador **no** regenera nada. Las anotaciones se conservan hasta que el item cambie, se suba la versión del procesador o se regeneren o borren desde `Application`.

### 4.3 Remezcla

Los remezcladores son un tipo de plugin propio. Leen items, anotaciones y artefactos de otros remezcladores y generan artefactos. Se ejecutan a mano, desde la CLI.

- **Cuándo regenerar** lo decide cada remezclador, en su siguiente ejecución. No hay invalidación ni marcas de obsolescencia, así que un artefacto puede estar desfasado respecto a sus items entre dos ejecuciones.
- Con el `updated_at` del artefacto y las fechas de los items, un remezclador puede ser incremental sin estado propio.
- **Artefacto requerido que no existe:** lo decide el remezclador (generar sin él o abortar). Los ciclos entre artefactos son responsabilidad de los remezcladores: cada uno lee la versión anterior del otro.

## 5. API: clase `Application`

Punto único de entrada para las herramientas externas: una API de Python que se usa en el mismo proceso, no un servicio de red. Ofrece:

- **Consulta** de items, anotaciones y artefactos. La consulta de un artefacto inexistente devuelve "no existe" de forma explícita.
- **Ejecución** de cada una de las tres fases (importar, enriquecer, remezclar). Enriquecer ejecuta todos los procesadores configurados, en el orden del YAML.
- **Regeneración forzada** de anotaciones, que reinicia el contador de intentos.
- **Borrado** de anotaciones, por procesador, por item o ambos. Borrar también elimina el estado de procesado, así que el item vuelve a quedar pendiente con los intentos a cero.

La base de datos no se expone: toda consulta pasa por `Application`.

## 6. Almacenamiento

- **Items:** contenido en disco mediante `foundation.storage.DiskStorage`, con su sha256 como clave. Los metadatos van en la base de datos (título, URI, tipo MIME, `content_sha256`, `data`, `published_at`, `modified_at`).
- **Estado de procesado:** en la base de datos, por `(item, procesador)`: estado, intentos, último error, versión del procesador y `content_sha256` usado.
- **Anotaciones y artefactos:** el contenido se guarda en disco mediante `foundation.storage.DiskStorage` y la base de datos guarda la referencia que esta devuelva. Los metadatos son:
  - Anotación: productor, item de referencia, clave, `created_at` y `updated_at`.
  - Artefacto: productor, nombre, tipo de contenido, `created_at` y `updated_at`.

## 7. Limitaciones conocidas

1. Los duplicados entre fuentes se procesan dos veces, con el coste que eso supone para procesadores caros.
2. Renombrar el `id` de una fuente deja huérfanos los items anteriores y reimporta todo con otra clave.
3. Los artefactos pueden estar desfasados entre dos ejecuciones de su remezclador.
4. Los items de una fuente retirada siguen apareciendo en los artefactos salvo que el remezclador los filtre.
5. Un item cuyo procesador de origen lo descarta nunca llega a los procesadores que dependen de él, y no queda registro de ello en esos procesadores.

## 8. Suposiciones confirmadas

1. `Application` es una API de Python que se usa en el mismo proceso, no un servicio de red.
2. Al borrar una anotación se elimina el estado de procesado y, con él, el contador de intentos.
