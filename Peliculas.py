import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Buscador de Películas Chinguis", layout="wide")

EXCEL_FILE = "peliculas_series.xlsx"
EDITABLE_COLS = ["¿Mugui?", "¿Punti?"]  # únicas columnas editables

# ---------- utilidades ----------
def leer_excel(path: str) -> pd.DataFrame:
    # Carga “fresca” (sin cache) para que siempre lea lo último
    df = pd.read_excel(path)
    # Normalizar tipos
    for col in EDITABLE_COLS:
        if col not in df.columns:
            df[col] = False
        df[col] = df[col].fillna(False).astype(bool)
    # Asegurar tipos numéricos (evita “Invalid number” al ordenar)
    for col in ["Año", "Duración", "Rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # ID estable para mapear cambios aunque se filtre/ordene
    if "_row_id" not in df.columns:
        df["_row_id"] = df.index.astype(int)
    return df

def guardar_excel_seguro(df: pd.DataFrame, path: str, reintentos: int = 3, espera_s: float = 0.4) -> None:
    # Evita errores tipo EOFError si hay escrituras concurrentes
    for i in range(reintentos):
        try:
            df.to_excel(path, index=False)
            return
        except Exception:
            time.sleep(espera_s)
    # último intento (si falla, dejamos pasar sin romper la app)
    try:
        df.to_excel(path, index=False)
    except Exception:
        pass

# ---------- carga base ----------
df_base = leer_excel(EXCEL_FILE)

# ---------- filtros (sidebar) ----------
st.sidebar.title("🎬 Filtros")

# Género
generos_sel = st.sidebar.multiselect(
    "Género",
    options=sorted(df_base["Género"].dropna().unique()) if "Género" in df_base.columns else []
)

# Plataformas únicas separando por ';'
if "Plataforma" in df_base.columns:
    plataformas_unicas = sorted(
        {p.strip() for v in df_base["Plataforma"].dropna() for p in str(v).split(";") if p.strip()}
    )
else:
    plataformas_unicas = []

plataformas_sel = st.sidebar.multiselect("Plataforma", options=plataformas_unicas)

# Rango de años
if "Año" in df_base.columns and not df_base["Año"].dropna().empty:
    anio_min, anio_max = int(df_base["Año"].min()), int(df_base["Año"].max())
else:
    anio_min, anio_max = 1900, 2100
rango_anios = st.sidebar.slider("Año", min_value=anio_min, max_value=anio_max, value=(anio_min, anio_max))

# Excluir vistos
excluir_mugui = st.sidebar.checkbox("❌ Excluir vistas por Mugui")
excluir_punti = st.sidebar.checkbox("❌ Excluir vistas por Punti")

# Orden
orden_col = st.sidebar.selectbox("Ordenar por", ["Nombre", "Año", "Duración", "Rating"])
orden_asc = st.sidebar.radio("Dirección", ["Ascendente", "Descendente"]) == "Ascendente"

# ---------- aplicar filtros sobre df_base (NO mostrar tabla todavía) ----------
df_filtrado = df_base.copy()

if generos_sel and "Género" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Género"].isin(generos_sel)]

if plataformas_sel and "Plataforma" in df_filtrado.columns:
    df_filtrado = df_filtrado[
        df_filtrado["Plataforma"].fillna("").apply(
            lambda cell: any(p in [s.strip() for s in str(cell).split(";")] for p in plataformas_sel)
        )
    ]

if "Año" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Año"].between(rango_anios[0], rango_anios[1])]

# Excluir (se aplica sobre el filtrado)
if excluir_mugui and "¿Mugui?" in df_filtrado.columns:
    df_filtrado = df_filtrado[~df_filtrado["¿Mugui?"]]
if excluir_punti and "¿Punti?" in df_filtrado.columns:
    df_filtrado = df_filtrado[~df_filtrado["¿Punti?"]]

# Ordenar seguro
if orden_col in df_filtrado.columns:
    try:
        df_filtrado = df_filtrado.sort_values(by=orden_col, ascending=orden_asc, kind="mergesort")
    except Exception:
        pass

# ---------- UI ----------
st.markdown("<h1 style='text-align:center'>🎥 Buscador de Películas Chinguis</h1>", unsafe_allow_html=True)
st.markdown(f"### 🔍 Se encontraron **{len(df_filtrado)}** películas")

# Mostrar SOLO la tabla filtrada, con edición en ¿Mugui? y ¿Punti?
# Ocultamos el _row_id pero lo mantenemos para poder guardar los cambios correctamente.
columnas_visibles = [c for c in df_filtrado.columns if c != "_row_id"]
edited = st.data_editor(
    df_filtrado[columnas_visibles + ["_row_id"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "¿Mugui?": st.column_config.CheckboxColumn("¿Mugui?"),
        "¿Punti?": st.column_config.CheckboxColumn("¿Punti?"),
        "_row_id": st.column_config.TextColumn("_row_id", help="interno", disabled=True)
    },
    disabled=[c for c in columnas_visibles if c not in EDITABLE_COLS],
    key="tabla_filtrada"
)

# ---------- detectar y guardar cambios SOLO en filas editadas ----------
# Tomamos solo columnas editables + _row_id
slice_new = edited[EDITABLE_COLS + ["_row_id"]].copy()
slice_old = df_base[EDITABLE_COLS + ["_row_id"]].copy()

# Unimos por _row_id para comparar valores antiguos vs nuevos (solo en las filas visibles/filtradas)
cmp = slice_new.merge(slice_old, on="_row_id", suffixes=("_new", "_old"), how="left")

# Filas donde cambió alguna editable
cambio_mask = False
for col in EDITABLE_COLS:
    m = cmp[f"{col}_new"] != cmp[f"{col}_old"]
    cambio_mask = m if isinstance(cambio_mask, bool) else (cambio_mask | m)

if not isinstance(cambio_mask, bool) and cambio_mask.any():
    # actualizamos df_base con los nuevos valores usando _row_id
    cambios = slice_new.loc[cambio_mask, ["_row_id"] + EDITABLE_COLS].copy()
    base_idx = df_base.set_index("_row_id")
    base_idx.update(cambios.set_index("_row_id"))
    df_actualizado = base_idx.reset_index()

    # Guardar de forma segura
    guardar_excel_seguro(df_actualizado, EXCEL_FILE)

# ---------- Botón: película al azar (sobre lo filtrado actual) ----------
if st.button("🍿 Mostrar una película al azar"):
    if not df_filtrado.empty:
        peli = df_filtrado.sample(1).iloc[0]
        st.markdown(
            f"""
            ### 🍿 Película sugerida:
            - 🎬 **Nombre:** {peli.get('Nombre','')}
            - 📅 **Año:** {peli.get('Año','')}
            - ⏱️ **Duración:** {peli.get('Duración','')} min
            - ⭐ **Rating:** {peli.get('Rating','')}
            - 📺 **Plataforma:** {peli.get('Plataforma','')}
            """
        )
    else:
        st.info("No hay películas que coincidan con los filtros actuales.")
