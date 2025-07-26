import streamlit as st
import pandas as pd

# Configurar diseño
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>🎬 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

# Cargar datos
df = pd.read_excel("peliculas_series.xlsx")

# Limpiar columnas no útiles
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.dropna(subset=["Nombre"])
df.columns = df.columns.str.strip()

# Asegurar que Mugui y Punti estén como booleanos
for col in ["¿Mugui?", "¿Punti?"]:
    if col not in df.columns:
        df[col] = False
    df[col] = df[col].fillna(False).astype(bool)

# Filtros
with st.sidebar:
    st.header("🎯 Filtros")

    # Género
    generos = df["Género"].dropna().unique()
    genero_sel = st.multiselect("Género", options=generos)

    # Plataforma
    plataformas = df["Plataforma"].dropna().unique()
    plataforma_sel = st.multiselect("Plataforma", options=plataformas)

    # Año
    año_min = int(df["Año"].min())
    año_max = int(df["Año"].max())
    año_sel = st.slider("Año", min_value=año_min, max_value=año_max, value=(año_min, año_max))

    # Exclusión
    excl_mugui = st.checkbox("❌ Excluir vistas por Mugui")
    excl_punti = st.checkbox("❌ Excluir vistas por Punti")

    # Orden
    orden_col = st.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
    orden_asc = st.radio("Orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()

if genero_sel:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(genero_sel)]

if plataforma_sel:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(plataforma_sel)]

df_filtrado = df_filtrado[df_filtrado["Año"].between(año_sel[0], año_sel[1])]

if excl_mugui:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"] == False]

if excl_punti:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"] == False]

# Ordenar
df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)

# Editor de tabla
st.subheader("📋 Lista de películas (puedes editar quién las vio)")
editable = st.data_editor(
    df_filtrado,
    use_container_width=True,
    column_config={
        "¿Mugui?": st.column_config.CheckboxColumn("¿Mugui?"),
        "¿Punti?": st.column_config.CheckboxColumn("¿Punti?")
    },
    disabled=["Nombre", "Año", "Duración", "Género", "Plataforma", "Rating"],
    num_rows="dynamic"
)

# Película al azar
if st.button("🎲 Sugerir una película al azar"):
    if not editable.empty:
        peli = editable.sample(1).iloc[0]
        st.markdown("### 🎲 Película sugerida:")
        st.markdown(f"**🎞️ Nombre:** {peli['Nombre']}")
        st.markdown(f"**📅 Año:** {peli['Año']}")
        st.markdown(f"**🕒 Duración:** {peli['Duración']} min")
        st.markdown(f"**⭐ Rating:** {peli['Rating']}")
        st.markdown(f"**📺 Plataforma:** {peli['Plataforma']}")
    else:
        st.warning("No hay películas con esos filtros.")

