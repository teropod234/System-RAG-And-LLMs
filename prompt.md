Respuesta de un prompt anterior: Con lo que tienes ahora, el siguiente paso no es montar el agente ni Chroma todavía. Primero hay que cerrar una pieza de datos.

Lo que tienes hoy
Products_clean.csv tiene catálogo (nombre, precio, rating, categoría), pero no tiene texto de reseñas — solo Review_Count como número. El RAG necesita texto para buscar cosas como “se calienta” o “buena batería”.

En raw/ sí tienes DatafinitiElectronicsProductData.csv, que trae reviews.text. Ese (o un dataset con descripciones/reseñas) será tu corpus para el vectorial.

Qué hacer primero (en orden)
1. Elige qué datasets usas y para qué
Apunta en un papel (o un .md tuyo) algo así:

Dataset	Para qué lo uso
Products_clean (o similar)
Precio, stock, ID → SQLite
Datafiniti (reseñas)
Texto de opiniones → Chroma / RAG
Hasta que no tengas claro esto, el resto se enreda.

2. Termina de limpiar el dataset con texto
Limpia al menos un CSV con reseñas o descripciones (Datafiniti es el candidato) y guárdalo en src/data/clean/.

Pregunta clave: ¿qué columna(s) usaré como texto para el RAG?
Ejemplo en Datafiniti: reviews.text, reviews.title, name, categories.

3. Crea la base relacional (SQLite)
Antes de embeddings, monta una tabla simple de productos con:

product_id
nombre
precio
stock (puedes inventarlo si no existe)
categoria
Carga ahí los datos estructurados de tus CSV limpios. Esto será la Tool 2 del enunciado (filtro estricto de precio/stock).

4. Recién entonces: chunking + embeddings + Chroma
Solo con el texto limpio:

Partir el texto en trozos (chunking).
Generar embeddings (OpenAI u Ollama).
Guardar en ChromaDB.
Eso será la Tool 1 (búsqueda semántica).

Resumen en una frase
Primero: limpia un dataset con texto de reseñas y define qué va a SQLite (números) y qué va al vectorial (texto).
Después: SQLite → Chroma → agente → Pydantic → Streamlit.

Señal de que vas bien
Puedes responder sí a estas tres preguntas:

¿Qué columna uso como product_id común?
¿Qué texto indexo en Chroma?
¿Dónde consulto precio/stock de forma exacta?
Si quieres, en el siguiente mensaje dime qué CSV vas a usar para reseñas y te ayudo solo a definir el esquema (columnas + tablas), sin escribir el código por ti.

- Prompt que te paso: vale, te he pasado el resultado de la terminal del ultimo paso por si te puede servir, pero ahora vamos a por el ultimo paso, no?? vamos por el paso E

Orden recomendado (sin saltarte pasos)
Paso A — Tool 2: funciones MySQL (antes del agente)
El agente no puede “adivinar” SQL. Necesitas 2–3 funciones Python claras, por ejemplo:

get_product_by_id(product_id) → precio y stock exactos
filter_products(max_price, min_stock, category?) → lista de productos que cumplen
Prueba cada una en un script suelto antes de enchufarlas al agente.

Objetivo: que con max_price=500 devuelva solo productos reales de tu tabla products.

Paso B — Tool 1: envolver Chroma
Ya tienes semantic_search() en src/model/vectorstore.py. Falta exponerla como tool con nombre y descripción que el LLM entienda, por ejemplo:

Nombre: buscar_opiniones_usuarios
Descripción: “Usa esto cuando la pregunta hable de opiniones, calidad, recomendaciones, experiencia de uso…”
Paso C — Modelo Pydantic de respuesta
Define antes el agente el contrato de salida:

producto_recomendado
pros_segun_usuarios
contras_tecnicos
precio_actual
puntuacion_confianza
Así el LLM no responde texto libre: responde JSON validado.

Paso D — Agente LangChain + Gemini
Monta un agente que:

Recibe la pregunta del usuario
Decide qué tool llamar (o ambas)
Combina resultados (reseñas de Chroma + datos duros de MySQL)
Devuelve el Pydantic del paso C
Flujo típico para: “Algo de audio recomendable por menos de 600 €”:

Usuario pregunta
    → Tool 1: opiniones sobre audio / recomendable
    → Tool 2: productos Audio con price < 600 y stock > 0
    → Cruza resultados
    → JSON Pydantic con recomendación
Paso E — Streamlit (último)
Cuando el agente funcione en consola:

Campo de texto para la pregunta
Panel con pasos del agente (qué tools llamó)
Tarjeta bonita con el JSON final
Resumen visual
[A] Funciones MySQL          ← empieza aquí
[B] Tool Chroma (wrapper)
[C] Pydantic
[D] Agente Gemini + tools
[E] Streamlit
Dónde poner el código (sugerencia)
src/db/queries.py      → Tool 2 (MySQL)
src/model/tools.py     → Tool 1 (wrapper Chroma)
src/agent/schemas.py   → Pydantic
src/agent/agent.py     → agente
src/scripts/run_agent.py  → probar en terminal
app.py o src/scripts/app_streamlit.py  → UI (al final)
Cómo saber que el agente va bien (sin Streamlit)
Ejecutas algo como:

"Busco un producto de audio recomendable por usuarios y que cueste menos de 600 dólares"
Y obtienes un JSON con producto real de tu BD, pros sacados de reseñas, y precio coherente con MySQL.

resultado del ultimo paso:

(Test_RAG) PS C:\Users\juanp\OneDrive\Documentos\GitHub\Test_RAG> uv run python src/scripts/run_agent.py
Modo: agente + Gemini
Modelo: gemini-2.5-flash
Consulta: Busco un producto de audio recomendable por usuarios y que cueste menos de 600 dólares

=== Pasos del agente ===
-> Llamó `filtrar_catalogo_productos` con {'category': 'Audio', 'max_price': 600}
<- Resultado `filtrar_catalogo_productos`: - AZ1010 | Smart Watch Model-27 | Audio | $35.02 | stock=83 | rating=4.9 | recomendado=sí
- AZ1014 | Power Bank Model-58 | Audio | $321.92 | stock=220 | rating=4.9 | recomendado=sí
- AZ1085 | External SSD Model-77 | Audi...
-> Llamó `buscar_opiniones_usuarios` con {'consulta': 'opiniones de usuarios sobre Smart Watch Model-27'}
<- Resultado `buscar_opiniones_usuarios`: [1] product_id=AZ1010
    producto: Smart Watch Model-27
    categoría: Audio | marca: Adobe | rating: 4.9
    autor reseña: Pablo Martínez | recomendado: True
    texto: Producto: Smart Watch Model-27
Categoría: Audio
M...
-> Llamó `RecomendacionProducto` con {'categoria': 'Audio', 'stock_disponible': 83, 'puntuacion_confianza': 0.9, 'precio_actual': 35.02, 'contras_tecnicos': ['No se encontraron contras específicos en las reseñas de usuarios. Sin embargo, al ser un Smart Watch, sus funcionalidades de audio podrían ser limitadas en comparación con dispositivos de audio dedicados.'], 'pros_segun_usuarios': ['Buen rendimiento y acabados de calidad.'], 'product_id': 'AZ1010', 'producto_recomendado': 'Smart Watch Model-27'}
<- Resultado `RecomendacionProducto`: Returning structured response: producto_recomendado='Smart Watch Model-27' pros_segun_usuarios=['Buen rendimiento y acabados de calidad.'] contras_tecnicos=['No se encontraron contras específicos en las reseñas de usuari...

=== Recomendación (JSON) ===
{
  "producto_recomendado": "Smart Watch Model-27",
  "pros_segun_usuarios": [
    "Buen rendimiento y acabados de calidad."
  ],
  "contras_tecnicos": [
    "No se encontraron contras específicos en las reseñas de usuarios. Sin embargo, al ser un Smart Watch, sus funcionalidades de audio podrían ser limitadas en comparación con dispositivos de audio dedicados."
  ],
  "precio_actual": 35.02,
  "puntuacion_confianza": 0.9,
  "product_id": "AZ1010",
  "categoria": "Audio",
  "stock_disponible": 83
}
(Test_RAG) PS C:\Users\juanp\OneDrive\Documentos\GitHub\Test_RAG> uv run python src/scripts/test_gemini_api.py
API key cargada: AIza...H0yU
Modelo en .env (GEMINI_MODEL): gemini-2.5-flash

=== Prueba generate_content por modelo ===

[OK] gemini-2.5-flash
       respuesta: OK

[OK] gemini-2.5-flash-lite
       respuesta: OK

[FALLO] gemini-2.0-flash-lite
       cuota agotada o free tier = 0 para este modelo

[FALLO] gemini-2.0-flash
       cuota agotada o free tier = 0 para este modelo

[FALLO] gemini-1.5-flash
       modelo no disponible con tu cuenta

Modelos que funcionan ahora:
  - gemini-2.5-flash
  - gemini-2.5-flash-lite