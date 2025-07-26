import streamlit as st
import pandas as pd
import random

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_excel("peliculas_series.xlsx")
    df["¿Mugui?"] = df["¿Mugui?"].fillna(False).astype(bool)
    df["¿Punti?"] = df["¿Punti?"].fillna(False).astype(bool)
    return df

# Guardar cambios
def guardar_datos(df):
    df.to_excel("peliculas_series.xlsx", index=False)

# Datos originales
df_original = cargar_datos()

# Sidebar
st.sidebar.markdown("## 🎬 Filtros")
generos = df_original["Género"].dropna().unique()
plataformas = df_original["Plataforma"].dropna().unique()
años_min = int(df_original["Año"].min())
años_max = int(df_original["Año"].max())

genero_sel = st.sidebar.multiselect("Género", generos)
plataforma_sel = st.sidebar.multiselect("Plataforma", plataformas)
año_sel = st.sidebar.slider("Año", años_min, años_max, (años_min, años_max))
excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

orden_col = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
orden_asc = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df_original.copy()
if genero_sel:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero_sel)]
if plataforma_sel:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataforma_sel)]
df_filtrado = df_filtrado[df_filtrado["Año"].between(año_sel[0], año_sel[1])]

# Editor de columnas editables
st.markdown("### 🎞️ Buscador de Películas Chinguis")

editable_cols = ["¿Mugui?", "¿Punti?"]
otros_cols = [col for col in df_filtrado.columns if col not in editable_cols]

# Editor (sin mostrar mensajes)
edited = st.data_editor(
    df_filtrado,
    column_config={
        "¿Mugui?": st.column_config.CheckboxColumn("¿Mugui?"),
        "¿Punti?": st.column_config.CheckboxColumn("¿Punti?")
    },
    disabled=otros_cols,
    use_container_width=True,
    hide_index=True
)

# Verificar y guardar si hay cambios en columnas editables
for col in editable_cols:
    if not edited[col].equals(df_filtrado[col]):
        df_original.update(edited[["Nombre", col]])
        guardar_datos(df_original)
        break  # Guarda una vez y sale

# Aplicar filtro nuevamente después de posibles cambios
df_filtrado = df_original.copy()
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
    except Exception:
        pass  # No mostrar nada

# Mostrar botón de película aleatoria
if not df_filtrado.empty:
    if st.button("🍿 Mostrar una película al azar"):
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown("### 🍿 Película sugerida:")
        st.markdown(f"🎬 **Nombre:** {peli['Nombre']}")
        st.markdown(f"📅 **Año:** {peli['Año']}")
        st.markdown(f"⏱️ **Duración:** {peli['Duración']} min")
        st.markdown(f"⭐ **Rating:** {peli['Rating']}")
        st.markdown(f"📺 **Plataforma:** {peli['Plataforma']}")
