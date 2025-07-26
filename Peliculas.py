import streamlit as st
import pandas as pd

# Cargar datos
df = pd.read_excel("peliculas_series.xlsx")

# Eliminar columnas sin nombre
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.dropna(subset=["Nombre"])

# Normalizar nombres
df.columns = df.columns.str.strip()

# Eliminar columnas no deseadas
df = df.drop(columns=["¿La vimos?", "Saga"], errors="ignore")

# Configuración de la página
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>🎥 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)

# Filtros en la barra lateral
with st.sidebar:
    st.header("🎯 Filtros")

    # Género
    if "Género" in df.columns:
        generos = df["Género"].dropna().unique()
        filtro_genero = st.multiselect("Género", options=generos)
    else:
        filtro_genero = []

    # Plataforma
    if "Plataforma" in df.columns:
        plataformas = df["Plataforma"].dropna().unique()
        filtro_plataforma = st.multiselect("Plataforma", options=plataformas)
    else:
        filtro_plataforma = []

    # Año
    if "Año" in df.columns:
        año_min = int(df["Año"].min())
        año_max = int(df["Año"].max())
        año_sel = st.slider("Año", min_value=año_min, max_value=año_max, value=(año_min, año_max))
    else:
        año_sel = (1900, 2100)

    # Exclusión por visto
    excl_mugui = st.checkbox("❌ Excluir películas que vio Mugui")
    excl_punti = st.checkbox("❌ Excluir películas que vio Punti")

    # Ordenamiento
    orden_col = st.selectbox("Ordenar por", ["Año", "Duración", "Rating"])
    orden_asc = st.radio("Dirección del orden", ["Ascendente", "Descendente"]) == "Ascendente"

# Aplicar filtros
df_filtrado = df.copy()

if filtro_genero:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(filtro_genero)]

if filtro_plataforma:
    df_filtrado = df_filtrado[df_filtrado["Plataforma"].isin(filtro_plataforma)]

if "Año" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Año"].between(año_sel[0], año_sel[1])]

# Corrección del filtro por películas vistas
if excl_mugui and "¿Mugui?" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["¿Mugui?"].astype(str).str.lower() != "sí"]

if excl_punti and "¿Punti?" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["¿Punti?"].astype(str).str.lower() != "sí"]

# Ordenar
df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc)

# Mostrar tabla centrada
st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Botón película al azar
if st.button("🎲 Sugerir una película al azar de las filtradas"):
    if not df_filtrado.empty:
        p = df_filtrado.sample(1).iloc[0]
        st.markdown("### 🎲 Película sugerida:")
        st.markdown(f"**🎞️ Nombre:** {p['Nombre']}")
        st.markdown(f"**📅 Año:** {p['Año']}")
        st.markdown(f"**🕒 Duración:** {p['Duración']} min")
        st.markdown(f"**⭐ Rating:** {p['Rating']}")
        st.markdown(f"**📺 Plataforma:** {p['Plataforma']}")
    else:
        st.warning("No hay películas disponibles con los filtros seleccionados.")
