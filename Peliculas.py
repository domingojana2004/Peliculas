import streamlit as st
import pandas as pd
import random
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    return pd.read_excel("peliculas_series.xlsx")

df = cargar_datos()

# --- BARRA LATERAL DE FILTROS ---
with st.sidebar:
    st.markdown("## 🎬 Filtros")
    genero_sel = st.multiselect("Género", sorted(df["Género"].dropna().unique()))
    plataforma_sel = st.multiselect("Plataforma", sorted(df["Plataforma"].dropna().unique()))
    año_sel = st.slider("Año", int(df["Año"].min()), int(df["Año"].max()), (int(df["Año"].min()), int(df["Año"].max())))
    excluir_mugui = st.checkbox("❌ Excluir vistas por Mugui")
    excluir_punti = st.checkbox("❌ Excluir vistas por Punti")
    orden_col = st.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
    orden_asc = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# --- FILTRADO DE DATOS ---
df_filtrado = df.copy()

if genero_sel:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero_sel)]
if plataforma_sel:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataforma_sel)]

df_filtrado = df_filtrado[df_filtrado["Año"].between(año_sel[0], año_sel[1])]

# Aseguramos columnas booleanas sin NaN
for col in ["¿Mugui?", "¿Punti?"]:
    if col in df_filtrado.columns:
        df_filtrado[col] = df_filtrado[col].fillna(False).astype(bool)

if excluir_mugui:
    df_filtrado = df_filtrado[~df_filtrado["¿Mugui?"]]
if excluir_punti:
    df_filtrado = df_filtrado[~df_filtrado["¿Punti?"]]

# --- ORDENAMIENTO SEGURO ---
try:
    df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)
except Exception:
    pass  # si hay error, no ordena pero tampoco rompe la app

# --- INTERFAZ PRINCIPAL ---
st.markdown("## 🎥 Buscador de Películas Chinguis")

# --- CONFIGURAR AGGRID ---
editable_cols = ["¿Mugui?", "¿Punti?"]
gb = GridOptionsBuilder.from_dataframe(df_filtrado)
for col in df_filtrado.columns:
    gb.configure_column(col, editable=(col in editable_cols))
gb.configure_grid_options(domLayout='normal')
gb.configure_selection(selection_mode="single", use_checkbox=False)

grid_response = AgGrid(
    df_filtrado,
    gridOptions=gb.build(),
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    height=350,
)

# --- GUARDAR CAMBIOS SI HAY ---
df_actualizado = grid_response["data"]
if not df_actualizado.equals(df):
    df.update(df_actualizado)
    df.to_excel("peliculas_series.xlsx", index=False)

# --- BOTÓN PARA PELÍCULA ALEATORIA ---
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown("### 🍿 Película sugerida:")
        st.markdown(f"🎬 **Nombre**: {peli['Nombre']}")
        st.markdown(f"📅 **Año**: {peli['Año']}")
        st.markdown(f"⏱️ **Duración**: {peli['Duración']} minutos")
        st.markdown(f"⭐ **Rating**: {peli['Rating']}")
        st.markdown(f"📺 **Plataforma**: {peli['Plataforma']}")
    else:
        st.warning("No hay películas que coincidan con los filtros.")
