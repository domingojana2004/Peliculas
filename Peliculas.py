import streamlit as st
import pandas as pd

# Cargar datos
df = pd.read_excel("peliculas_series.xlsx")
df.columns = df.columns.str.strip()

# Eliminar columnas que no se usarán
df = df.drop(columns=["¿La vi yo?", "¿La vio ella?"], errors="ignore")

# Título
st.markdown("<h1 style='text-align: center;'>🎬 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎯 Filtros")
generos = df["Género"].dropna().unique()
plataformas = df["Plataforma"].dropna().unique()
año_min, año_max = int(df["Año"].min()), int(df["Año"].max())

genero_filtro = st.sidebar.multiselect("Género", sorted(generos))
plataforma_filtro = st.sidebar.multiselect("Plataforma", sorted(plataformas))
año_filtro = st.sidebar.slider("Año", min_value=año_min, max_value=año_max, value=(año_min, año_max))

excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

orden_col = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
orden_asc = st.sidebar.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()

if genero_filtro:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero_filtro)]

if plataforma_filtro:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataforma_filtro)]

df_filtrado = df_filtrado[df_filtrado["Año"].between(año_filtro[0], año_filtro[1])]

if excluir_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] != True]

if excluir_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] != True]

# Ordenamiento seguro
try:
    if orden_col in df_filtrado.columns:
        df_filtrado = df_filtrado.dropna(subset=[orden_col])
        df_filtrado[orden_col] = df_filtrado[orden_col].astype(str) if orden_col == "Nombre" else df_filtrado[orden_col]
        df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)
except Exception:
    pass  # Silenciar el error sin mostrar advertencias

# Mostrar tabla editable solo en columnas de checkboxes
df_filtrado.reset_index(drop=True, inplace=True)
df_editable = df_filtrado.copy()
df_editable[["¿Mugui?", "¿Punti?"]] = df_editable[["¿Mugui?", "¿Punti?"]].astype(bool)

editado = st.data_editor(
    df_editable,
    use_container_width=True,
    hide_index=True,
    disabled=df_editable.columns.difference(["¿Mugui?", "¿Punti?"]).tolist(),  # bloquear todas menos esas 2
    column_config={
        "¿Mugui?": st.column_config.CheckboxColumn("¿Mugui?"),
        "¿Punti?": st.column_config.CheckboxColumn("¿Punti?")
    }
)

# Película al azar
if not df_filtrado.empty and st.button("🎲 Mostrar una película al azar"):
    peli = df_filtrado.sample(1).iloc[0]
    st.markdown("### 🍿 Película sugerida:")
    st.markdown(f"**🎬 Nombre:** {peli['Nombre']}")
    st.markdown(f"📆 **Año:** {peli['Año']}")
    st.markdown(f"⏱️ **Duración:** {peli['Duración']}")
    st.markdown(f"⭐ **Rating:** {peli['Rating']}")
    st.markdown(f"📺 **Plataforma:** {peli['Plataforma']}")
elif df_filtrado.empty:
    st.warning("⚠️ No hay películas con los filtros actuales.")
