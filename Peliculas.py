import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

EXCEL_FILE = "peliculas_series.xlsx"

# --- CARGAR Y GUARDAR ---
def cargar_datos():
    return pd.read_excel(EXCEL_FILE)

def guardar_datos(dataframe):
    dataframe.to_excel(EXCEL_FILE, index=False)

# Cargamos df original
df = cargar_datos()

# --- SIDEBAR FILTROS ---
st.sidebar.title("🎬 Filtros")

generos = st.sidebar.multiselect("Género", options=df["Género"].dropna().unique())

plataformas_unicas = sorted(
    {p.strip() for sublist in df["Plataforma"].dropna() for p in str(sublist).split(";")}
)
plataformas = st.sidebar.multiselect("Plataforma", options=plataformas_unicas)

min_year, max_year = int(df["Año"].min()), int(df["Año"].max())
rango_anos = st.sidebar.slider("Año", min_year, max_year, (min_year, max_year))

excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

orden_columna = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
ascendente = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# --- TABLA EDITABLE (ANTES DE FILTRAR) ---
st.markdown("<h1 style='text-align: center;'>🎥 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

editable_cols = ["¿Mugui?", "¿Punti?"]

edited_df = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={col: st.column_config.CheckboxColumn() for col in editable_cols},
    disabled=[col for col in df.columns if col not in editable_cols],
    key="editor"
)

# --- GUARDAR CAMBIOS DE TICKS ---
if not edited_df.equals(df):
    guardar_datos(edited_df)
    df = edited_df.copy()  # Actualizamos el df original con los cambios

# --- APLICAR FILTROS ---
df_filtrado = df.copy()

if generos:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(generos)]

if plataformas:
    df_filtrado = df_filtrado[
        df_filtrado["Plataforma"].apply(
            lambda x: any(p in str(x).split(";") for p in plataformas)
        )
    ]

df_filtrado = df_filtrado[
    (df_filtrado["Año"] >= rango_anos[0]) & (df_filtrado["Año"] <= rango_anos[1])
]

if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] != True]

if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] != True]

try:
    df_filtrado = df_filtrado.sort_values(by=orden_columna, ascending=ascendente)
except:
    pass

st.markdown(f"### 🔍 Se encontraron **{len(df_filtrado)}** películas")

# --- BOTÓN ALEATORIO ---
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown(
            f"""
            ### 🍿 Película sugerida:
            - 🎬 **Nombre:** {peli['Nombre']}
            - 📅 **Año:** {peli['Año']}
            - ⏱️ **Duración:** {peli['Duración']} min
            - ⭐ **Rating:** {peli['Rating']}
            - 📺 **Plataforma:** {peli['Plataforma']}
            """
        )
    else:
        st.warning("No hay películas que coincidan con los filtros.")
