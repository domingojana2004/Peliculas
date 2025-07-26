import streamlit as st
import pandas as pd
import random

# Cargar datos
df = pd.read_excel("peliculas_series.xlsx")

# Normalizar nombres de columnas
df.columns = df.columns.str.strip()

# Eliminar columnas finales
df = df.drop(columns=["¿La vio ella?", "¿La vi yo?"], errors="ignore")

# Título
st.markdown("<h1 style='text-align: center;'>🎬 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

# Sidebar para filtros
st.sidebar.markdown("## 🎯 Filtros")

generos = df['Género'].dropna().unique()
plataformas = df['Plataforma'].dropna().unique()
año_min, año_max = int(df['Año'].min()), int(df['Año'].max())

genero_seleccionado = st.sidebar.multiselect("Género", sorted(generos))
plataforma_seleccionada = st.sidebar.multiselect("Plataforma", sorted(plataformas))
rango_anio = st.sidebar.slider("Año", min_value=año_min, max_value=año_max, value=(año_min, año_max))

# Filtros por vistos
excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

# Ordenamiento
orden_col = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
orden_asc = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()

if genero_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['Género'].isin(genero_seleccionado)]

if plataforma_seleccionada:
    df_filtrado = df_filtrado[df_filtrado['Plataforma'].isin(plataforma_seleccionada)]

df_filtrado = df_filtrado[df_filtrado['Año'].between(rango_anio[0], rango_anio[1])]

if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado['¿Mugui?'] != True]

if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado['¿Punti?'] != True]

# Ordenar si la columna existe
if orden_col in df_filtrado.columns:
    df_filtrado = df_filtrado.dropna(subset=[orden_col])
    df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)

# Editar columnas ¿Mugui? y ¿Punti?
df_filtrado.reset_index(drop=True, inplace=True)
df_editable = df_filtrado.copy()
df_editable[['¿Mugui?', '¿Punti?']] = df_editable[['¿Mugui?', '¿Punti?']].astype(bool)
editado = st.data_editor(
    df_editable,
    use_container_width=True,
    hide_index=True,
    column_config={
        "¿Mugui?": st.column_config.CheckboxColumn("¿Mugui?"),
        "¿Punti?": st.column_config.CheckboxColumn("¿Punti?")
    }
)

# Película al azar
if not df_filtrado.empty:
    if st.button("🎲 Mostrar una película al azar"):
        pelicula_azar = df_filtrado.sample(1).iloc[0]
        st.markdown("### 🍿 Película sugerida:")
        st.markdown(f"**🎬 Nombre:** {pelicula_azar['Nombre']}")
        st.markdown(f"📆 **Año:** {pelicula_azar['Año']}")
        st.markdown(f"⏱️ **Duración:** {pelicula_azar['Duración']}")
        st.markdown(f"⭐ **Rating:** {pelicula_azar['Rating']}")
        st.markdown(f"📺 **Plataforma:** {pelicula_azar['Plataforma']}")
else:
    st.warning("No hay películas que coincidan con los filtros.")

# Mostrar tabla
st.markdown("### 📋 Películas filtradas:")
st.dataframe(df_filtrado, use_container_width=True)
