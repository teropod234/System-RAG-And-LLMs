Enunciado del Proyecto: "InsightMarket AI" - Agente Inteligente de Análisis de Mercado y Recomendación de Productos
📝 Contexto del problema
Las empresas de e-commerce y análisis de mercado reciben miles de reseñas de usuarios y especificaciones de productos técnicos diariamente. Los analistas de negocio y los equipos de soporte necesitan una herramienta que no solo responda preguntas basadas en el catálogo de productos, sino que sea capaz de analizar el sentimiento de las opiniones, cruzarlo con datos técnicos del inventario y recomendar productos de forma proactiva actuando como un consultor experto.

🚀 Tu Misión (Objetivos Técnicos)
Vas a construir un Agente RAG Avanzado que actúe como un analista experto. El sistema debe ser capaz de recibir la consulta de un usuario (ej: "Busco un portátil para programar IA, que no se caliente mucho según los usuarios y que cueste menos de 1200€"), decidir qué herramientas usar, extraer la información técnica y de opiniones, y redactar un informe ejecutivo con recomendaciones.

🛠️ Arquitectura y Tecnologías Requeridas
Para que un reclutador flipe, el proyecto debe implementar obligatoriamente esta pila tecnológica:

Ingesta de Datos y Vectorización (La base del RAG):

Diseña un dataset sintético o usa uno público de productos (electrónica, ropa, etc.) que contenga especificaciones técnicas y texto de reseñas de usuarios.

Procesa el texto, divídelo en fragmentos (chunking) y genera embeddings utilizando una API (como text-embedding-3-small de OpenAI o un modelo local de HuggingFace/Ollama).

Almacena estos embeddings en una Base de Datos Vectorial (puedes usar ChromaDB, FAISS o la extensión pgvector de PostgreSQL si quieres lucirte con SQL).

El Sistema de Agente (LangChain / LlamaIndex / CrewAI):

No hagas un RAG simple. Configura un Agente que tenga acceso a herramientas (Tools).

El agente debe tener, como mínimo, dos herramientas:

Tool 1 (Búsqueda Semántica): Busca en la base de datos vectorial el contexto de las reseñas de los usuarios (ej: qué opina la gente sobre la batería o la temperatura).

Tool 2 (Filtro Estricto/API): Una función de Python que consulte una base de datos relacional tradicional o simule una API para comprobar el precio exacto y el stock actual en tiempo real.

Razonamiento y Salida Estructurada (Pydantic + LLM API):

Usa una API de LLM comercial (OpenAI, Anthropic) o un modelo local potente a través de Ollama.

Obliga al LLM a devolver la respuesta final en un formato JSON estructurado utilizando Pydantic (con campos como: producto_recomendado, pros_segun_usuarios, contras_tecnicos, precio_actual, puntuacion_confianza).

Interfaz de Usuario (Streamlit):

Crea un dashboard interactivo donde el usuario/reclutador pueda escribir su consulta y ver el "pensamiento" del agente en tiempo real (los pasos que toma) antes de mostrar el resultado final maquetado de forma limpia.