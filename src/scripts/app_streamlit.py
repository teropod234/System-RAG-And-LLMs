"""
Paso E — InsightMarket AI (Streamlit).

    uv run streamlit run src/scripts/app_streamlit.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.agent.agent import ejecutar_agente
from src.agent.config import get_gemini_model_name
from src.agent.demo import ejecutar_agente_demo
from src.agent.schemas import RecomendacionProducto

st.set_page_config(
    page_title="InsightMarket AI",
    page_icon="📊",
    layout="wide",
)

EJEMPLO_CONSULTA = (
    "Busco un producto de audio recomendable por usuarios "
    "y que cueste menos de 600 dólares"
)


def _render_recomendacion(rec: RecomendacionProducto) -> None:
    st.subheader(rec.producto_recomendado)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio (USD)", f"${rec.precio_actual:,.2f}")
    col2.metric("Confianza", f"{rec.puntuacion_confianza:.0%}")
    col3.metric("Stock", rec.stock_disponible if rec.stock_disponible is not None else "—")
    col4.metric("Categoría", rec.categoria or "—")

    if rec.product_id:
        st.caption(f"ID producto: `{rec.product_id}`")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Pros según usuarios**")
        for pro in rec.pros_segun_usuarios:
            st.success(pro)
    with c2:
        st.markdown("**Contras / limitaciones**")
        for contra in rec.contras_tecnicos:
            st.warning(contra)

    with st.expander("JSON completo"):
        st.json(rec.model_dump())


def main() -> None:
    st.title("InsightMarket AI")
    st.caption("Consultor RAG: reseñas (Chroma) + catálogo exacto (MySQL)")

    with st.sidebar:
        st.header("Opciones")
        modo_demo = st.toggle(
            "Modo demo (sin Gemini)",
            help="Usa solo las tools si Gemini no tiene cuota (error 429).",
        )
        if not modo_demo:
            st.info(f"Modelo: `{get_gemini_model_name()}`")
        st.markdown("---")
        st.markdown(
            "**Requisitos**\n"
            "- MySQL con productos cargados\n"
            "- Chroma indexado (`build_vectorstore.py`)\n"
            "- `GOOGLE_API_KEY` en `.env` (salvo modo demo)"
        )

    consulta = st.text_area(
        "Tu consulta",
        value=EJEMPLO_CONSULTA,
        height=100,
        placeholder="Ej: portátil para programar, buenas reseñas, menos de 800 USD",
    )

    ejecutar = st.button("Obtener recomendación", type="primary", use_container_width=True)

    if ejecutar:
        if not consulta.strip():
            st.error("Escribe una consulta antes de continuar.")
            return

        with st.spinner("El agente está analizando catálogo y reseñas..."):
            try:
                resultado = (
                    ejecutar_agente_demo(consulta)
                    if modo_demo
                    else ejecutar_agente(consulta)
                )
            except Exception as exc:
                msg = str(exc)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    st.error(
                        "Cuota de Gemini agotada (429). Activa **Modo demo** en el sidebar "
                        "o cambia `GEMINI_MODEL=gemini-2.5-flash` en `.env`."
                    )
                else:
                    st.error(f"Error al ejecutar el agente: {exc}")
                return

        st.markdown("---")
        st.markdown("### Pensamiento del agente")
        if resultado.pasos:
            for i, paso in enumerate(resultado.pasos, start=1):
                with st.expander(f"Paso {i}", expanded=i <= 2):
                    st.code(paso, language=None)
        else:
            st.info("No se registraron pasos intermedios.")

        st.markdown("---")
        st.markdown("### Informe ejecutivo")
        _render_recomendacion(resultado.recomendacion)


if __name__ == "__main__":
    main()
