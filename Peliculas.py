import streamlit as st
import pandas as pd

# Cargar datos
df = pd.read_excel("peliculas_series.xlsx")

# Eliminar columnas "La vi yo" y "La vio ella" si existen
df = df.drop(columns=["La vi yo", "La vio ella"], errors="ignore")

# Título
st.title("🎬 Buscador de Películas Chinguis")

# Filtros de género
generos = df["Género"].dropna().unique()
filtro_genero = st.multiselect("Filtrar por género", generos)

# Filtros de plataforma
plataformas = df["Plataformas"].dropna().unique()
filtro_plataforma = st.multiselect("Filtrar por plataforma", plataformas)

# Rango de año
min_anio = int(df["Año"].min())
max_anio = int(df["Año"].max())
rango_anio = st.slider("Filtrar por año", min_anio, max_anio, (min_anio, max_anio))

# Filtro: excluir películas vistas por Mugui y/o Punti
excluir_mugui = st.checkbox("Excluir películas vistas por Mugui")
excluir_punti = st.checkbox("Excluir películas vistas por Punti")

# Ordenar por columna
ordenar_por = st.selectbox("Ordenar por:", ["Año", "Duración", "Rating"])
orden_asc = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()

if filtro_genero:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(filtro_genero)]

if filtro_plataforma:
    df_filtrado = df_filtrado[df_filtrado["Plataformas"].isin(filtro_plataforma)]

df_filtrado = df_filtrado[(df_filtrado["Año"] >= rango_anio[0]) & (df_filtrado["Año"] <= rango_anio[1])]

if excluir_mugui and "Mugui" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Mugui"] != "Sí"]

if excluir_punti and "Punti" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Punti"] != "Sí"]

# Ordenar
df_filtrado = df_filtrado.sort_values(by=ordenar_por, ascending=orden_asc)

# Mostrar tabla
st.dataframe(df_filtrado.reset_index(drop=True))

# Botón para guardar cambios
if st.button("💾 Guardar cambios"):
    df_editado.to_excel(archivo_guardado, index=False)
    st.success(f"¡Cambios guardados en {archivo_guardado}!")
