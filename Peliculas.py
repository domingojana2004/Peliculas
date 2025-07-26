import streamlit as st
import pandas as pd
import random

# Configuración de la página
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>🎬 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_excel("peliculas_series.xlsx")
    df["¿Mugui?"] = df["¿Mugui?"].fillna(False).astype(bool)
    df["¿Punti?"] = df["¿Punti?"].fillna(False).astype(bool)
    df["Año"] = pd.to_numeric(df["Año"], errors="coerce")
    return df

df = cargar_datos()

# Sidebar
st.sidebar.markdown("### 🎬 Filtros")

# Filtros
generos = st.sidebar.multiselect("Género", options=sorted(df["Género"].dropna().unique()))
plataformas = st.sidebar.multiselect("Plataforma", options=sorted(df["Plataforma"].dropna().unique()))
año_min, año_max = int(df["Año"].min()), int(df["Año"].max())
rango_año = st.sidebar.slider("Año", min_value=año_min, max_value=año_max, value=(año_min, año_max))

excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

orden_col = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
orden_asc = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Filtro
df_filtrado = df.copy()
if generos:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(generos)]
if plataformas:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataformas)]
df_filtrado = df_filtrado[(df_filtrado["Año"] >= rango_año[0]) & (df_filtrado["Año"] <= rango_año[1])]
if excluir_mugui:
    df_filtrado = df_filtrado[~df_filtrado["¿Mugui?"]]
if excluir_punti:
    df_filtrado = df_filtrado[~df_filtrado["¿Punti?"]]

# Ordenar sin errores de tipos mezclados
try:
    df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)
except Exception:
    pass  # Evita errores si hay tipos mezclados

# Mostrar tabla centrada
st.markdown("### ")
col1, col2, col3 = st.columns([0.2, 1, 0.2])
with col2:
    st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)

# Película al azar
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        pelicula_azar = df_filtrado.sample(1).iloc[0]
        st.markdown("### 🍿 Película sugerida:")
        st.markdown(f"🎬 **Nombre:** {pelicula
