import streamlit as st
import pandas as pd
import random

# Cargar datos
df = pd.read_excel("peliculas_series.xlsx")

# Eliminar columnas no deseadas
df = df.drop(columns=["¿La vimos?", "Saga"], errors="ignore")

# Título
st.title("🎬 Buscador de Películas Chinguis")

# Filtros
st.subheader("🎯 Filtros")

# Filtro por género
generos = df["Género"].dropna().unique()
filtro_genero = st.multiselect("Filtrar por género", options=generos)

# Filtro por plataforma
plataformas = df["Plataforma"].dropna().unique()
filtro_plataforma = st.multiselect("Filtrar por plataforma", options=plataformas)

# Filtro por año
min_anio = int(df["Año"].min())
max_anio = int(df["Año"].max())
rango_anio = st.slider("Filtrar por año", min_value=min_anio, max_value=max_anio, value=(min_anio, max_anio))

# Excluir películas vistas por Mugui o Punti
excluir_mugui = st.checkbox("Excluir películas que vio Mugui")
excluir_punti = st.checkbox("Excluir películas que vio Punti")

# Orden
orden_opcion = st.selectbox("Ordenar por", ["Año", "Duración", "Rating"])

# Aplicar filtros
df_filtrado = df.copy()

if filtro_genero:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(filtro_genero)]

if filtro_plataforma:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(filtro_plataforma)]

df_filtrado = df_filtrado[df_filtrado["Año"].between(rango_anio[0], rango_anio[1])]

if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] != "Sí"]

if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] != "Sí"]

# Ordenar
df_filtrado = df_filtrado.sort_values(by=orden_opcion)

# Mostrar resultados
st.subheader("🎥 Películas encontradas")
st.dataframe(df_filtrado.reset_index(drop=True))

# Película al azar
if st.button("🎲 Sugerir una película al azar"):
    if not df_filtrado.empty:
        seleccion = df_filtrado.sample(1).iloc[0]
        st.success(f"🎞️ **{seleccion['Nombre']}**\n\n📅 Año: {seleccion['Año']}\n🕒 Duración: {seleccion['Duración']} min\n⭐ Rating: {seleccion['Rating']}\n📺 Plataforma: {seleccion['Plataforma']}")
    else:
        st.warning("No hay películas disponibles con los filtros seleccionados.")
