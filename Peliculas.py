import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

# Cargar el Excel
@st.cache_data
def cargar_datos():
    return pd.read_excel("peliculas_series.xlsx")

df = cargar_datos()

# Filtros en barra lateral
st.sidebar.title("🎬 Filtros")

generos = st.sidebar.multiselect(
    "Género", options=df["Género"].dropna().unique()
)

plataformas = st.sidebar.multiselect(
    "Plataforma", options=df["Plataforma"].dropna().unique()
)

min_year, max_year = int(df["Año"].min()), int(df["Año"].max())
rango_anos = st.sidebar.slider("Año", min_year, max_year, (min_year, max_year))

excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

# Ordenar
orden_columna = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
ascendente = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# --- Filtrado ---
df_filtrado = df.copy()

if generos:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(generos)]

if plataformas:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataformas)]

df_filtrado = df_filtrado[
    (df_filtrado["Año"] >= rango_anos[0]) & (df_filtrado["Año"] <= rango_anos[1])
]

if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] != True]

if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] != True]

# --- Ordenar sin romper ---
if orden_columna in df_filtrado.columns:
    try:
        df_filtrado = df_filtrado.sort_values(by=orden_columna, ascending=ascendente)
    except Exception as e:
        st.warning(f"No se pudo ordenar por '{orden_columna}': {e}")

# Mostrar título
st.markdown("<h2 style='text-align: center;'>🎥 Buscador de Películas Chinguis</h2>", unsafe_allow_html=True)

# Mostrar tabla editable SOLO columnas Mugui y Punti
edit_cols = ["¿Mugui?", "¿Punti?"]

# Creamos un dataframe solo con esas columnas como editables
df_editable = st.data_editor(
    df_filtrado,
    column_config={col: st.column_config.CheckboxColumn(default=False) for col in edit_cols},
    disabled=[col for col in df_filtrado.columns if col not in edit_cols],
    hide_index=True
)

# Botón para película al azar
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        peli_random = df_filtrado.sample(1).iloc[0]
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:20px;">
                <h3>🍿 Película sugerida:</h3>
                <p><b>🎬 Nombre:</b> {peli_random['Nombre']}</p>
                <p><b>📅 Año:</b> {peli_random['Año']}</p>
                <p><b>⭐ Rating:</b> {peli_random['Rating']}</p>
                <p><b>⏱️ Duración:</b> {peli_random['Duración']} min</p>
                <p><b>📺 Plataforma:</b> {peli_random['Plataforma']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("⚠️ No hay películas para mostrar.")
