import streamlit as st
import pandas as pd
import random
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Cargar datos desde Excel
excel_path = "peliculas_series.xlsx"
df = pd.read_excel(excel_path)

# Asegurarse que las columnas booleans estén como tal
for col in ["¿Mugui?", "¿Punti?", "¿La vimos?"]:
    if col in df.columns:
        df[col] = df[col].astype(bool)

# Título
st.markdown("## 🎬 Buscador de Películas Chinguis")

# Sidebar con filtros
with st.sidebar:
    st.markdown("### 🎯 Filtros")
    genero = st.multiselect("Género", options=df["Género"].dropna().unique())
    plataforma = st.multiselect("Plataforma", options=df["Plataforma"].dropna().unique())
    año_range = st.slider("Año", int(df["Año"].min()), int(df["Año"].max()), (int(df["Año"].min()), int(df["Año"].max())))
    excluir_mugui = st.checkbox("❌ Excluir vistas por Mugui")
    excluir_punti = st.checkbox("❌ Excluir vistas por Punti")
    orden_col = st.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
    orden_asc = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()
if genero:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero)]
if plataforma:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataforma)]
df_filtrado = df_filtrado[(df_filtrado["Año"] >= año_range[0]) & (df_filtrado["Año"] <= año_range[1])]
if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] == False]
if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] == False]
try:
    df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)
except:
    pass

# Tabla editable en columnas específicas
gb = GridOptionsBuilder.from_dataframe(df_filtrado)
for col in df_filtrado.columns:
    editable = col in ["¿Mugui?", "¿Punti?", "¿La vimos?"]
    gb.configure_column(col, editable=editable)
grid_options = gb.build()

response = AgGrid(
    df_filtrado,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MANUAL,
    fit_columns_on_grid_load=True,
    height=400,
    allow_unsafe_jscode=True,
)

# Guardar si hay cambios
df_actualizado = response["data"]
if not df_actualizado.equals(df_filtrado):
    for idx, row in df_actualizado.iterrows():
        df.loc[df["Nombre"] == row["Nombre"], ["¿Mugui?", "¿Punti?", "¿La vimos?"]] = row[["¿Mugui?", "¿Punti?", "¿La vimos?"]]
    df.to_excel(excel_path, index=False)

# Mostrar película sugerida
if st.button("🍿 Mostrar una película al azar") and not df_filtrado.empty:
    peli = df_filtrado.sample(1).iloc[0]
    st.markdown("### 🍿 Película sugerida:")
    st.markdown(f"- 🎬 **Nombre:** {peli['Nombre']}")
    st.markdown(f"- 🗓️ **Año:** {peli['Año']}")
    st.markdown(f"- ⏱️ **Duración:** {peli['Duración']} minutos")
    st.markdown(f"- ⭐ **Rating:** {peli['Rating']}")
    st.markdown(f"- 📺 **Plataforma:** {peli['Plataforma']}")


