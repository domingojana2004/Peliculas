import streamlit as st
import pandas as pd
import random

# Cargar los datos
df = pd.read_excel("peliculas_series.xlsx")

# Eliminar columnas sin nombre o vacías
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.dropna(subset=["Nombre"])

# Normalizar nombres de columnas
df.columns = df.columns.str.strip().str.capitalize()

# Eliminar columnas finales innecesarias si existen
for col in ["La vi yo", "La vio ella"]:
    if col in df.columns:
        df.drop(columns=col, inplace=True)

# Sidebar con filtros
with st.sidebar:
    st.header("🎬 Filtros")
    
    # Filtro por género
    generos = df["Género"].dropna().unique()
    genero_sel = st.multiselect("Filtrar por género", options=generos)

    # Filtro por plataforma
    plataformas = df["Plataforma"].dropna().unique()
    plataforma_sel = st.multiselect("Filtrar por plataforma", options=plataformas)

    # Filtro por año
    año_min = int(df["Año"].min())
    año_max = int(df["Año"].max())
    año_sel = st.slider("Año de lanzamiento", año_min, año_max, (año_min, año_max))

    # Filtros de exclusión
    excl_mugui = st.checkbox("❌ Excluir películas vistas por Mugui")
    excl_punti = st.checkbox("❌ Excluir películas vistas por Punti")

    # Ordenamiento
    orden = st.selectbox("Ordenar por", options=["Año", "Duración", "Rating"])

# Aplicar filtros
filtro = df.copy()

if genero_sel:
    filtro = filtro[filtro["Género"].isin(genero_sel)]

if plataforma_sel:
    filtro = filtro[filtro["Plataforma"].isin(plataforma_sel)]

filtro = filtro[(filtro["Año"] >= año_sel[0]) & (filtro["Año"] <= año_sel[1])]

if excl_mugui and "Mugui" in filtro.columns:
    filtro = filtro[filtro["Mugui"] != "✅"]

if excl_punti and "Punti" in filtro.columns:
    filtro = filtro[filtro["Punti"] != "✅"]

# Ordenar
filtro = filtro.sort_values(by=orden, ascending=True)

# Título centrado
st.markdown("<h1 style='text-align: center;'>🎥 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

# Mostrar tabla centrada
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.dataframe(filtro.reset_index(drop=True), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Película aleatoria
if st.button("🎲 Dame una película al azar de la lista filtrada"):
    if not filtro.empty:
        p = filtro.sample(1).iloc[0]
        st.markdown("### 🎲 Película aleatoria sugerida:")
        st.markdown(f"**🎞️ Nombre:** {p['Nombre']}")
        st.markdown(f"**📅 Año:** {p['Año']}")
        st.markdown(f"**🕒 Duración:** {p['Duración']} min")
        st.markdown(f"**⭐ Rating:** {p['Rating']}")
        st.markdown(f"**📺 Plataforma:** {p['Plataforma']}")
    else:
        st.warning("No hay películas que coincidan con los filtros.")
