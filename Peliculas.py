import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

# Cargar datos
df = pd.read_excel("peliculas_series.xlsx")

# Renombrar columnas para trabajar sin errores
df.columns = df.columns.str.strip()

# Opciones únicas
generos = sorted(df["Género"].dropna().unique())
plataformas = sorted(df["Plataforma"].dropna().unique())
ordenables = ["Nombre", "Duración", "Rating", "Año"]

# Sidebar de filtros
with st.sidebar:
    st.markdown("### 🎬 Filtros")

    genero_selec = st.multiselect("Género", generos)
    plataforma_selec = st.multiselect("Plataforma", plataformas)

    año_min = int(df["Año"].min())
    año_max = int(df["Año"].max())
    año_rango = st.slider("Año", año_min, año_max, (año_min, año_max))

    excluir_mugui = st.checkbox("❌ Excluir vistas por Mugui")
    excluir_punti = st.checkbox("❌ Excluir vistas por Punti")

    orden_col = st.selectbox("Ordenar por", ordenables)
    orden_asc = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

st.markdown("<h1 style='text-align: center;'>🎬 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

# Aplicar filtros
df_filtrado = df.copy()

if genero_selec:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero_selec)]

if plataforma_selec:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataforma_selec)]

df_filtrado = df_filtrado[df_filtrado["Año"].between(año_rango[0], año_rango[1])]

if excluir_mugui and "¿Mugui?" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] != True]

if excluir_punti and "¿Punti?" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] != True]

# Ordenar si la columna es válida y no está vacía
if orden_col in df_filtrado.columns:
    df_filtrado = df_filtrado.dropna(subset=[orden_col])
    df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)
else:
    st.warning(f"La columna '{orden_col}' no se encontró en los datos.")

# Mostrar botón para obtener película al azar
st.subheader("🎲 Sugerencia aleatoria")
if st.button("Dame una película al azar"):
    if not df_filtrado.empty:
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown(f"""
        **🎬 {peli['Nombre']}**  
        📅 Año: {peli['Año']}  
        ⏱️ Duración: {peli['Duración']} min  
        ⭐ Rating: {peli['Rating']}  
        📺 Plataforma: {peli['Plataforma']}
        """)
    else:
        st.info("No hay películas que cumplan con esos filtros.")

# Mostrar tabla editable y centrada
st.markdown("### 🎞️ Lista de Películas Filtradas")
cols = [col for col in df_filtrado.columns if col not in ["la vi yo", "la vio ella"]]

edited_df = st.data_editor(
    df_filtrado[cols],
    use_container_width=True,
    column_config={
        "¿Mugui?": st.column_config.CheckboxColumn("¿Mugui?"),
        "¿Punti?": st.column_config.CheckboxColumn("¿Punti?")
    },
    num_rows="dynamic",
    hide_index=True
)
