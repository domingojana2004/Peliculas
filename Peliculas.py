import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="🎬 Películas vistas", layout="wide")

# Ruta del archivo
archivo_excel = "peliculas_series.xlsx"
archivo_guardado = "peliculas_actualizadas.xlsx"

# Cargar datos
if os.path.exists(archivo_excel):
    df = pd.read_excel(archivo_excel)
else:
    st.error("No se encontró el archivo peliculas_series.xlsx")
    st.stop()

# Agregar columnas de seguimiento si no existen
if "¿La vi yo?" not in df.columns:
    df["¿La vi yo?"] = False
if "¿La vio otra persona?" not in df.columns:
    df["¿La vio otra persona?"] = False

st.title("🎬 Catálogo de Películas Compartido")

# Editar tabla
df_editado = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    disabled=["Nombre", "Año", "Género", "Plataforma"]
)

# Botón para guardar cambios
if st.button("💾 Guardar cambios"):
    df_editado.to_excel(archivo_guardado, index=False)
    st.success(f"¡Cambios guardados en {archivo_guardado}!")
