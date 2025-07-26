import requests
import pandas as pd
import time

API_TMDB = "18a7968890f673989b5a5b2f12adaae1"
PAIS = "CL"

# Leer las películas desde el archivo Excel
df = pd.read_excel("peliculas_series.xlsx")
titulos = df["Nombre"].astype(str).tolist()

def buscar_id_tmdb(titulo):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": API_TMDB, "query": titulo}
    response = requests.get(url, params=params).json()
    resultados = response.get("results")
    return resultados[0]["id"] if resultados else None

def obtener_plataformas(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/watch/providers"
    params = {"api_key": API_TMDB}
    response = requests.get(url, params=params).json()
    try:
        data = response["results"][PAIS]["flatrate"]
        return "; ".join([p["provider_name"] for p in data]) if data else "No disponible"
    except KeyError:
        return "No disponible"

# Recorremos todas las películas
plataformas_finales = []
for titulo in titulos:
    print(f"🔍 Buscando: {titulo}")
    tmdb_id = buscar_id_tmdb(titulo)
    plataformas = obtener_plataformas(tmdb_id) if tmdb_id else "No disponible"
    plataformas_finales.append(plataformas)
    print(f"✅ {titulo} → {plataformas}")
    time.sleep(0.25)  # para no sobrecargar la API

# Agregamos columna y guardamos
df["Plataformas"] = plataformas_finales
df.to_excel("peliculas_series_con_plataformas.xlsx", index=False)
print("\n🎉 Archivo guardado como 'peliculas_series_con_plataformas.xlsx'")
