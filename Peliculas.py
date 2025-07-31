import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

# --- CARGAR Y GUARDAR DATOS ---
EXCEL_FILE = "peliculas_series.xlsx"

@st.cache_data
def cargar_datos():
    return pd.read_excel(EXCEL_FILE)

def guardar_datos(dataframe):
    dataframe.to_excel(EXCEL_FILE, index=False)

df = cargar_datos()

# --- SIDEBAR FILTROS ---
st.sidebar.title("🎬 Filtros")

generos = st.sidebar.multiselect("Género", options=df["Género"].dropna().unique())

# plataformas únicas limpiando combinadas
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

# --- APLICAR FILTROS SIN EXCLUIR AÚN ---
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

try:
    df_filtrado = df_filtrado.sort_values(by=orden_columna, ascending=ascendente)
except:
    pass

# --- MOSTRAR TABLA (EDITABLE ANTES DE EXCLUIR) ---
st.markdown("<h1 style='text-align: center;'>🎥 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)
st.markdown(f"### 🔍 Se encontraron **{len(df_filtrado)}** películas")

editable_cols = ["¿Mugui?", "¿Punti?"]

# Tabla editable
edited_df = st.data_editor(
    df_filtrado,
    use_container_width=True,
    hide_index=True,
    column_config={col: st.column_config.CheckboxColumn() for col in editable_cols},
    disabled=[col for col in df_filtrado.columns if col not in editable_cols],
    key="editor"
)

# --- GUARDAR LOS CAMBIOS ANTES DE EXCLUIR ---
for idx in edited_df.index:
    for col in editable_cols:
        if df.loc[idx, col] != edited_df.loc[idx, col]:
            df.loc[idx, col] = edited_df.loc[idx, col]

guardar_datos(df)

# --- APLICAR FILTRO DE EXCLUIR DESPUÉS ---
df_filtrado = edited_df.copy()

if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] != True]

if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] != True]

# --- BOTÓN PELÍCULA AL AZAR ---
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        pelicula = df_filtrado.sample(1).iloc[0]
        st.markdown(
            f"""
            ### 🍿 Película sugerida:
            - 🎬 **Nombre:** {pelicula['Nombre']}
            - 📅 **Año:** {pelicula['Año']}
            - ⏱️ **Duración:** {pelicula['Duración']} min
            - ⭐ **Rating:** {pelicula['Rating']}
            - 📺 **Plataforma:** {pelicula['Plataforma']}
            """
        )
    else:
        st.warning("No hay películas que coincidan con los filtros.")
