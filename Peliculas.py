import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

EXCEL_FILE = "peliculas_series.xlsx"

# --- Cargar datos ---
def cargar_datos():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        st.error(f"No se encontró el archivo {EXCEL_FILE}")
        return pd.DataFrame()

def guardar_datos(df):
    df.to_excel(EXCEL_FILE, index=False)

# Leemos el excel completo
df = cargar_datos()

# --- FILTROS ---
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

orden_columna = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
ascendente = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# --- FILTRADO ---
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

# --- ORDENAR ---
try:
    df_filtrado = df_filtrado.sort_values(by=orden_columna, ascending=ascendente)
except:
    pass

# --- TABLA EDITABLE ---
st.markdown("<h2 style='text-align: center;'>🎥 Buscador de Películas Chinguis</h2>", unsafe_allow_html=True)

edit_cols = ["¿Mugui?", "¿Punti?"]

df_editado = st.data_editor(
    df_filtrado,
    column_config={col: st.column_config.CheckboxColumn(default=False) for col in edit_cols},
    disabled=[c for c in df_filtrado.columns if c not in edit_cols],
    hide_index=True,
    key="tabla_peliculas"
)

# --- ACTUALIZAR CAMBIOS EN EL DATAFRAME ORIGINAL ---
if not df_editado.equals(df_filtrado):
    for idx in df_editado.index:
        df.loc[df.index == idx, edit_cols] = df_editado.loc[idx, edit_cols].values

    # Guardar los cambios en el Excel
    guardar_datos(df)

# --- BOTÓN ALEATORIO ---
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:20px;">
                <h3>🍿 Película sugerida:</h3>
                <p><b>🎬 Nombre:</b> {peli['Nombre']}</p>
                <p><b>📅 Año:</b> {peli['Año']}</p>
                <p><b>⭐ Rating:</b> {peli['Rating']}</p>
                <p><b>⏱️ Duración:</b> {peli['Duración']} min</p>
                <p><b>📺 Plataforma:</b> {peli['Plataforma']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("⚠️ No hay películas disponibles para mostrar.")
