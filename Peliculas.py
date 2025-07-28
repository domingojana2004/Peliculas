import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import random

st.set_page_config(layout="wide")

# Cargar datos
file_path = "peliculas_series.xlsx"
df = pd.read_excel(file_path)

# Convertir columnas booleanas
df["¿Mugui?"] = df["¿Mugui?"].astype(bool)
df["¿Punti?"] = df["¿Punti?"].astype(bool)

# Filtros
with st.sidebar:
    st.markdown("## 🎬 Filtros")
    generos = st.multiselect("Género", options=sorted(df["Género"].dropna().unique()))
    plataformas = st.multiselect("Plataforma", options=sorted(df["Plataforma"].dropna().unique()))
    min_year = int(df["Año"].min())
    max_year = int(df["Año"].max())
    year_range = st.slider("Año", min_year, max_year, (min_year, max_year))
    excluir_mugui = st.checkbox("❌ Excluir vistas por Mugui")
    excluir_punti = st.checkbox("❌ Excluir vistas por Punti")
    orden_columna = st.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
    ascendente = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()
if generos:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(generos)]
if plataformas:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].str.contains('|'.join(plataformas), na=False)]
df_filtrado = df_filtrado[(df_filtrado["Año"] >= year_range[0]) & (df_filtrado["Año"] <= year_range[1])]
if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] == False]
if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] == False]

# Ordenar
df_filtrado = df_filtrado.sort_values(by=orden_columna, ascending=ascendente)

# Mostrar tabla editable
st.markdown("## 🎥 Buscador de Películas Chinguis")

gb = GridOptionsBuilder.from_dataframe(df_filtrado)
gb.configure_column("¿Mugui?", editable=True)
gb.configure_column("¿Punti?", editable=True)
gb.configure_grid_options(domLayout='normal')
grid_response = AgGrid(
    df_filtrado,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=480
)

# Guardar cambios
df_actualizado = grid_response["data"]
df.update(df_actualizado.set_index("Nombre"), overwrite=True)
df.to_excel(file_path, index=False)

# Mostrar película aleatoria
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        pelicula = df_filtrado.sample(1).iloc[0]
        st.markdown(
            f"""
            **🎞️ Nombre:** {pelicula['Nombre']}  
            **📆 Año:** {pelicula['Año']}  
            **⏱️ Duración:** {pelicula['Duración']} minutos  
            **⭐ Rating:** {pelicula['Rating']}  
            **📺 Plataforma:** {pelicula['Plataforma']}
            """
        )

