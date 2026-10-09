# InsightMarket AI

Agente RAG de recomendación de productos para e-commerce. Recibe una consulta en lenguaje natural, cruza **opiniones de usuarios** (búsqueda semántica en ChromaDB) con **precio y stock exactos** (MySQL) y devuelve un informe ejecutivo en JSON validado con Pydantic.

Ejemplo de consulta:

> Busco un producto de audio recomendable por usuarios y que cueste menos de 600 dólares

## Arquitectura

```
Usuario (Streamlit / CLI)
        │
        ▼
Agente LangChain + Gemini
        │
        ├── Tool 1: buscar_opiniones_usuarios  → ChromaDB (reseñas)
        └── Tool 2: filtrar_catalogo / obtener_producto_por_id  → MySQL
        │
        ▼
RecomendacionProducto (Pydantic / JSON)
```

| Capa | Tecnología | Rol |
| --- | --- | --- |
| Datos | `Amazon_Big_Sales_Dataset_2026.csv` → `Products_clean.csv` | Catálogo + texto de reseñas |
| Relacional | MySQL (`products`) | Precio, stock, categoría, rating |
| Vectorial | ChromaDB + embeddings Gemini | Búsqueda semántica de opiniones |
| Agente | LangChain + Gemini | Decide qué tools usar y combina resultados |
| Salida | Pydantic | JSON estructurado obligatorio |
| UI | Streamlit | Consulta, pasos del agente e informe |

## Requisitos

- Python **3.13+** (el repo usa **3.14** en `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- MySQL en local
- Clave de [Google AI Studio](https://aistudio.google.com/) (`GOOGLE_API_KEY`)

## Instalación

```bash
git clone https://github.com/teropod234/Test_RAG.git
cd Test_RAG
uv sync
```

Copia las variables de entorno:

```bash
copy .env.example .env
```

En `.env` configura MySQL y Gemini:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=TU_PASSWORD
MYSQL_DATABASE=Rag_prueba

GOOGLE_API_KEY=tu_clave
GEMINI_MODEL=gemini-2.5-flash
```

## Pipeline de datos y modelo

Ejecuta los pasos **en este orden** la primera vez.

### 1. Limpiar el dataset

```bash
uv run python src/scripts/data_processing.py
```

Genera `src/data/clean/Products_clean.csv` a partir de `src/data/raw/Amazon_Big_Sales_Dataset_2026.csv`.

### 2. Cargar el catálogo en MySQL

```bash
uv run python src/scripts/load_products_mysql.py
```

Crea la base `Rag_prueba` (si no existe) y la tabla `products`.

### 3. Indexar reseñas en Chroma

```bash
uv run python src/scripts/build_vectorstore.py
```

El índice se guarda en `src/model/chroma_db/` (está en `.gitignore`).

Consulta de prueba sobre el índice:

```bash
uv run python src/scripts/build_vectorstore.py --query "buena batería"
```

## Uso

### Interfaz Streamlit (paso E)

```bash
uv run streamlit run src/scripts/app_streamlit.py
```

En la barra lateral hay un **modo demo** (sin Gemini) por si la API responde 429 por cuota.

### Agente en terminal

```bash
uv run python src/scripts/run_agent.py
uv run python src/scripts/run_agent.py --query "portátil recomendable por menos de 800 dólares"
uv run python src/scripts/run_agent.py --demo
```

La respuesta sigue el contrato `RecomendacionProducto`:

- `producto_recomendado`
- `pros_segun_usuarios`
- `contras_tecnicos`
- `precio_actual`
- `puntuacion_confianza`
- `product_id`, `categoria`, `stock_disponible` (opcionales)

### Scripts de apoyo

| Script | Qué hace |
| --- | --- |
| `src/scripts/test_mysql_queries.py` | Prueba filtros de catálogo (Tool 2) |
| `src/scripts/test_tools.py` | Prueba las tools del agente |
| `src/scripts/test_gemini_api.py` | Comprueba qué modelos Gemini responden |
| `src/scripts/eda.py` | EDA en Streamlit (`uv run streamlit run src/scripts/eda.py`) |

## Estructura del repositorio

```
src/
  agent/          # Agente, tools, esquema Pydantic, demo
  db/             # Conexión MySQL, esquema, loader, queries
  model/          # Embeddings, Chroma, wrapper de búsqueda
  scripts/        # Pipeline, tests y UI
  data/raw/       # CSV originales
  data/clean/     # CSV limpios
  utils/          # Limpieza de datos
  config/         # Rutas del proyecto
```

## Notas

- Los precios y el stock **no se inventan**: salen de MySQL.
- Los pros se basan en reseñas recuperadas de Chroma.
- El modelo por defecto es `gemini-2.5-flash`. Si hay cuota agotada, usa `--demo` o el toggle de Streamlit.
- El enunciado original está en [`enunciado.md`](enunciado.md).
