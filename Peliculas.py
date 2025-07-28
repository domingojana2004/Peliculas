import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import random

# Leer datos
df = pd.read_excel("peliculas_series.xlsx")

# Asegurar que los tipos de datos sean correctos
df['Año'] = pd.to_numeric(df['Año'], errors='coerce')
df['Duración'] = pd.to_numeric(df['Duración'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
df['¿Mugui?'] = df['¿Mugui?'].fillna(False).astype(bool)
df['¿Punti?'] = df['¿Punti?'].fillna(False).astype(bool)

# Sidebar: Filtros
st.sidebar.markdown("## 🎬 Filtros")

generos = st.sidebar.multiselect("Género", sorted(df['Género'].dropna().unique()))
plataformas = st.sidebar.multiselect("Plataforma", sorted(df['Plataforma'].dropna().unique()))
año_min, año_max = int(df['Año'].min()), int(df['Año'].max())
rango_años = st.sidebar.slider("Año", min_value=año_min, max_value=año_max, value=(año_min, año_max))
excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

ordenar_por = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
orden_ascendente = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()
if generos:
    df_filtrado = df_filtrado[df_filtrado['Género'].isin(generos)]
if plataformas:
    df_filtrado = df_filtrado[df_filtrado['Plataforma'].str.contains('|'.join(plataformas), na=False)]
df_filtrado = df_filtrado[(df_filtrado['Año'] >= rango_años[0]) & (df_filtrado['Año'] <= rango_años[1])]
if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado['¿Mugui?'] == False]
if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado['¿Punti?'] == False]

# Ordenar
if ordenar_por in df_filtrado.columns:
    df_filtrado = df_filtrado.sort_values(by=ordenar_por, ascending=orden_ascendente)

# Mostrar título
st.markdown("## 🎥 Buscador de Películas Chinguis")

# Mostrar tabla editable (solo columnas de checkboxes)
gb = GridOptionsBuilder.from_dataframe(df_filtrado)
gb.configure_column("¿Mugui?", editable=True, cellEditor='agCheckboxCellEditor')
gb.configure_column("¿Punti?", editable=True, cellEditor='agCheckboxCellEditor')
gb.configure_columns(
    [col for col in df_filtrado.columns if col not in ['¿Mugui?', '¿Punti?']],
    editable=False
)
grid_options = gb.build()

grid_response = AgGrid(
    df_filtrado,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    fit_columns_on_grid_load=True,
    height=450
)

# Guardar cambios
df_actualizado = grid_response['data']
if not df_actualizado.equals(df_filtrado):
    for idx, row in df_actualizado.iterrows():
        original_idx = df[df["Nombre"] == row["Nombre"]].index
        if not original_idx.empty:
            df.loc[original_idx, '¿Mugui?'] = row['¿Mugui?']
            df.loc[original_idx, '¿Punti?'] = row['¿Punti?']
    df.to_excel("peliculas_series.xlsx", index=False)

# Película al azar
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown(f"### 🍿 Película sugerida:")
        st.markdown(f"- 🎬 **Nombre:** {peli['Nombre']}")
        st.markdown(f"- 📅 **Año:** {peli['Año']}")
        st.markdown(f"- ⏱️ **Duración:** {peli['Duración']} min")
        st.markdown(f"- ⭐ **Rating:** {peli['Rating']}")
        st.markdown(f"-
