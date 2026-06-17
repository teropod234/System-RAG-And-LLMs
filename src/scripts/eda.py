"""
EDA en Streamlit: un bloque por CSV (rutas desde `src.config.paths`).

Ejecutar desde la raíz del repo:
    uv run streamlit run src/scripts/eda.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Raíz del proyecto en sys.path (Streamlit no siempre la incluye sola)
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.config.paths import list_clean_csv_paths, raw_data_dir_clean

sns.set_theme(style="whitegrid")


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def _categorical_columns(df: pd.DataFrame, max_cardinality: int = 40) -> list[str]:
    out: list[str] = []
    for col in df.columns:
        if df[col].dtype == "object" or str(df[col].dtype) == "category":
            nu = df[col].nunique(dropna=True)
            if 1 < nu <= max_cardinality:
                out.append(col)
    return out


def _plot_correlation_heatmap(df: pd.DataFrame) -> plt.Figure | None:
    num = _numeric_columns(df)
    if len(num) < 2:
        return None
    corr = df[num].corr(numeric_only=True)
    if corr.empty or corr.shape[0] < 2:
        return None
    fig, ax = plt.subplots(figsize=(min(14, 0.35 * len(num) + 4), min(12, 0.35 * len(num) + 4)))
    sns.heatmap(corr, annot=len(num) <= 12, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlación (columnas numéricas)")
    fig.tight_layout()
    return fig


def _plot_missing(df: pd.DataFrame) -> plt.Figure | None:
    miss = df.isnull().sum()
    miss = miss[miss > 0].sort_values(ascending=True)
    if miss.empty:
        return None
    fig, ax = plt.subplots(figsize=(8, max(3, 0.25 * len(miss))))
    miss.plot(kind="barh", ax=ax, color="coral")
    ax.set_title("Valores nulos por columna")
    fig.tight_layout()
    return fig


def _plot_numeric_histograms(df: pd.DataFrame, max_cols: int = 6) -> plt.Figure | None:
    num = _numeric_columns(df)
    if not num:
        return None
    cols = num[:max_cols]
    n = len(cols)
    nrows = (n + 1) // 2
    fig, axes = plt.subplots(nrows, 2, figsize=(10, 2.8 * nrows))
    axes = axes.flatten() if n > 1 else [axes]
    for i, c in enumerate(cols):
        axes[i].hist(df[c].dropna(), bins=30, color="steelblue", edgecolor="white")
        axes[i].set_title(c)
    for j in range(len(cols), len(axes)):
        axes[j].set_visible(False)
    fig.suptitle("Distribución (primeras columnas numéricas)", y=1.02)
    fig.tight_layout()
    return fig


def _plot_categorical_counts(df: pd.DataFrame, max_cols: int = 4) -> plt.Figure | None:
    cats = _categorical_columns(df)
    if not cats:
        return None
    cats = cats[:max_cols]
    n = len(cats)
    fig, axes = plt.subplots(n, 1, figsize=(9, 2.8 * n))
    if n == 1:
        axes = [axes]
    for ax, col in zip(axes, cats, strict=True):
        vc = df[col].value_counts().head(15)
        vc.plot(kind="barh", ax=ax, color="seagreen")
        ax.set_title(f"Top categorías — {col}")
    fig.suptitle("Frecuencias (categóricas con cardinalidad moderada)", y=1.01)
    fig.tight_layout()
    return fig


def _render_one_csv(path: Path) -> None:
    st.subheader(path.name)
    try:
        df = pd.read_csv(path)
    except Exception as e:
        st.error(f"No se pudo leer el CSV: {e}")
        return

    st.caption(f"Filas: **{len(df):,}** · Columnas: **{len(df.columns)}**")
    st.dataframe(df.head(20), use_container_width=True)

    st.markdown("#### `describe()`")
    st.dataframe(df.describe(include="all").transpose(), use_container_width=True)

    st.markdown("#### Resumen de tipos y nulos")
    info = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "nulos": df.isnull().sum(),
            "no_nulos": df.notna().sum(),
            "n_unique": df.nunique(dropna=True),
        }
    )
    st.dataframe(info, use_container_width=True)

    fig_miss = _plot_missing(df)
    if fig_miss is not None:
        st.markdown("#### Nulos")
        st.pyplot(fig_miss)
        plt.close(fig_miss)
    else:
        st.info("No hay columnas con valores nulos.")

    fig_hm = _plot_correlation_heatmap(df)
    if fig_hm is not None:
        st.markdown("#### Heatmap de correlación")
        st.pyplot(fig_hm)
        plt.close(fig_hm)
    else:
        st.info("Heatmap de correlación omitido: hacen falta al menos 2 columnas numéricas.")

    fig_hist = _plot_numeric_histograms(df)
    if fig_hist is not None:
        st.markdown("#### Histogramas (numéricas)")
        st.pyplot(fig_hist)
        plt.close(fig_hist)

    fig_cat = _plot_categorical_counts(df)
    if fig_cat is not None:
        st.markdown("#### Barras (categóricas)")
        st.pyplot(fig_cat)
        plt.close(fig_cat)


def main() -> None:
    st.set_page_config(page_title="EDA — InsightMarket", layout="wide")
    st.title("EDA por CSV")
    st.caption(f"Carpeta de datos: `{raw_data_dir_clean()}`")

    paths = list_clean_csv_paths()

    if not paths:
        st.warning(
            "No hay ningún `.csv` en la carpeta clean. Ejecuta primero el procesado, p. ej.:\n\n"
            "`uv run python src/scripts/data_processing.py`"
        )
        return

    tabs = st.tabs([p.name for p in paths])
    for tab, path in zip(tabs, paths, strict=True):
        with tab:
            _render_one_csv(path)


if __name__ == "__main__":
    main()
