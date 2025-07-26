import streamlit as st
import pandas as pd
import random
import os

# Cargar los datos
@st.cache_data
def cargar_datos():
    df = pd.read_excel("peliculas_series.xlsx")
    df["¿Mugui?"] = df["¿Mugui?"].fillna(False).astype(bool)
    df["¿Punti?"] = df["¿Punti?"].fillna(False).astype(bool)
    return df

df = cargar_datos()

# Sidebar con filtros
st.sidebar.markdown("## 🎬 Filtros")
generos = df["Género"].dropna().unique()
plataformas = df["Plataforma"].dropna().unique()
años_min = int(df["Año"].min())
años_max = int(df["Año"].max())

genero_sel = st.sidebar.multiselect("Género", generos)
plataforma_sel = st.sidebar.multiselect("Plataforma", plataformas)
año_sel = st.sidebar.slider("Año", min_value=años_min, max_value=años_max, value=(años_min, años_max))
excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

orden_col = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
orden_asc = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()

if genero_sel:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero_sel)]

if plataforma_sel:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataforma_sel)]

df_filtrado = df_filtrado[df_filtrado["Año"].between(año_sel[0], año_sel[1])]

if excluir_mugui:
    df_filtrado = df_filtrado[~df_filtrado["¿Mugui?"]]

if excluir_punti:
    df_filtrado = df_filtrado[~df_filtrado["¿Punti?"]]

# Ordenar
if orden_col in df_filtrado.columns:
    try:
        df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)
    except Exception as e:
        st.warning(f"No se pudo ordenar por '{orden_col}': {e}")

# Mostrar tabla editable SOLO columnas de check
st.markdown("### 🎞️ Buscador de Películas Chinguis")

edited_df = st.data_editor(
    df_filtrado,
    column_config={
        "¿Mugui?": st.column_config.CheckboxColumn("¿Mugui?"),
        "¿Punti?": st.column_config.CheckboxColumn("¿Punti?")
    },
    disabled=[col for col in df_filtrado.columns if col not in ["¿Mugui?", "¿Punti?"]],
    use_container_width=True,
    hide_index=True
)

# Guardar cambios en archivo original si hay edición
if not edited_df.equals(df_filtrado):
    df.update(edited_df)
    df.to_excel("peliculas_series.xlsx", index=False)
    st.success("✅ Cambios guardados en el archivo.")

# Mostrar una película aleatoria filtrada
if not df_filtrado.empty:
    if st.button("🍿 Mostrar una película al azar"):
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown("### 🍿 Película sugerida:")
        st.markdown(f"🎬 **Nombre:** {peli['Nombre']}")
        st.markdown(f"📅 **Año:** {peli['Año']}")
        st.markdown(f"⏱️ **Duración:** {peli['Duración']} min")
        st.markdown(f"⭐ **Rating:** {peli['Rating']}")
        st.markdown(f"📺 **Plataforma:** {peli['Plataforma']}")
else:
    st.info("No hay películas que cumplan con los filtros.")
