import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import random

# --- Configuración inicial ---
st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

# --- Cargar datos ---
df = pd.read_excel("peliculas_series.xlsx")

# --- Limpiar nombres de columnas por seguridad ---
df.columns = df.columns.str.strip()

# --- Convertir columnas necesarias a numéricas ---
for col in ["Año", "Duración", "Rating"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --- Sidebar con filtros ---
with st.sidebar:
    st.markdown("## 🎬 Filtros")
    
    generos = df["Género"].dropna().unique()
    genero_sel = st.multiselect("Género", generos)

    plataformas = sorted({p.strip() for v in df["Plataforma"].dropna() for p in str(v).split(";")})
    plataforma_sel = st.multiselect("Plataforma", plataformas)

    min_anio, max_anio = int(df["Año"].min()), int(df["Año"].max())
    anio_rango = st.slider("Año", min_anio, max_anio, (min_anio, max_anio))

    excluir_mugui = st.checkbox("❌ Excluir vistas por Mugui")
    excluir_punti = st.checkbox("❌ Excluir vistas por Punti")

    orden_columna = st.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
    ascendente = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# --- Aplicar filtros ---
df_filtrado = df.copy()

if genero_sel:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero_sel)]

if plataforma_sel:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].fillna("").apply(lambda x: any(p in x for p in plataforma_sel))]

df_filtrado = df_filtrado[(df_filtrado["Año"] >= anio_rango[0]) & (df_filtrado["Año"] <= anio_rango[1])]

if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] != True]

if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] != True]

# --- Ordenar sin error ---
if orden_columna in df_filtrado.columns:
    df_filtrado = df_filtrado.sort_values(by=orden_columna, ascending=ascendente)

# --- Título de la app ---
st.markdown("## 🎥 Buscador de Películas Chinguis")

# --- Tabla editable ---
gb = GridOptionsBuilder.from_dataframe(df_filtrado)
gb.configure_column("¿Mugui?", editable=True, checkbox=True)
gb.configure_column("¿Punti?", editable=True, checkbox=True)
grid_options = gb.build()

grid_response = AgGrid(
    df_filtrado,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MANUAL,
    height=500,
    fit_columns_on_grid_load=True
)

# --- Mostrar película aleatoria ---
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown(
            f"""
            ### 🎬 **Nombre:** {peli['Nombre']}
            - **Duración:** {peli['Duración']} min  
            - **Rating:** {peli['Rating']}  
            - **Año:** {peli['Año']}  
            - **Plataforma:** {peli['Plataforma']}
            """
        )
    else:
        st.warning("No hay películas que coincidan con los filtros.")
