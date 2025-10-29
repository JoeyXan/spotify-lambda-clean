"""
Módulo para descargar modelos desde GitHub Releases (método robusto)
Usa la API de GitHub para recuperar browser_download_url de los assets del release.
"""

import os
import requests
import pickle
import pandas as pd
import time
from pathlib import Path

GITHUB_USER = "JoeyXan"            
GITHUB_REPO = "spotify-lambda-clean"
RELEASE_TAG = "v1.0"

# Ajustes
MODELS_DIR = "models"
RETRY_TIMES = 3
RETRY_DELAY = 3  # segundos
MIN_PKL_BYTES = 400  # scaler.pkl tiene ~926 bytes — aceptar tamaños pequeños pero > MIN_PKL_BYTES

def get_release_assets(user, repo, tag):
    """
    Consulta la API de GitHub para obtener assets del release.
    Devuelve dict {filename: browser_download_url}
    """
    api_url = f"https://api.github.com/repos/{user}/{repo}/releases/tags/{tag}"
    print(f"Consultando GitHub API: {api_url}")
    try:
        r = requests.get(api_url, timeout=30)
        print(f" GitHub API status: {r.status_code}")
        r.raise_for_status()
        data = r.json()
        assets = data.get("assets", [])
        result = {}
        for a in assets:
            name = a.get("name")
            url = a.get("browser_download_url")
            size = a.get("size")
            print(f"  Asset encontrado: {name} ({size} bytes) -> {url}")
            result[name] = url
        return result
    except Exception as e:
        print(f" Error consultando release: {e}")
        return {}

def download_with_retries(url, dest_path, retries=RETRY_TIMES):
    """
    Descarga con reintentos y muestra progreso simple.
    """
    for attempt in range(1, retries+1):
        try:
            print(f"  Intento {attempt} descargar: {url}")
            with requests.get(url, stream=True, timeout=60) as r:
                print(f"   status_code: {r.status_code}")
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(dest_path, "wb") as f:
                    if total == 0:
                        # contenido pequeño o headers no proporcionan tamaño
                        content = r.content
                        f.write(content)
                        downloaded = len(content)
                    else:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                percent = (downloaded / total) * 100
                                print(f"    Progreso: {percent:.1f}% ({downloaded}/{total})", end="\r")
                print(f"\n   Descarga completada: {dest_path} ({downloaded} bytes)")
            return True
        except Exception as e:
            print(f"   Error en intento {attempt}: {e}")
            if attempt < retries:
                print(f"   Reintentando en {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                print("   Agotados reintentos.")
                return False

def ensure_models_downloaded(models_dir=MODELS_DIR):
    Path(models_dir).mkdir(parents=True, exist_ok=True)

    # Obtener assets vía API
    assets = get_release_assets(GITHUB_USER, GITHUB_REPO, RELEASE_TAG)
    if not assets:
        print("No se obtuvieron assets desde la API de GitHub. Verifica usuario/repo/tag o la conexión.")
        return False

    needed = ['scaler.pkl', 'similarity_matrix.pkl', 'processed_tracks.csv']
    for name in needed:
        if name not in assets:
            print(f"Error: el asset '{name}' no está en el Release {RELEASE_TAG}.")
            return False

    for filename in needed:
        url = assets[filename]
        filepath = os.path.join(models_dir, filename)
        # Si ya existe, revisamos tamaño rápido
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"{filename} ya existe localmente ({size} bytes).")
        else:
            print(f"Descargando {filename} ...")
            ok = download_with_retries(url, filepath)
            if not ok:
                print(f"Error descargando {filename}")
                # limpiar archivo parcialmente descargado
                if os.path.exists(filepath):
                    os.remove(filepath)
                return False

        # validación tamaño para archivos pkl
        if filename.endswith('.pkl'):
            size = os.path.getsize(filepath)
            print(f" Tamaño final de {filename}: {size} bytes")
            if size < MIN_PKL_BYTES:
                print(f" Error: {filename} parece muy pequeño ({size} bytes). Se requiere al menos {MIN_PKL_BYTES} bytes.")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return False

    return True

def load_models(models_dir=MODELS_DIR):
    """
    Llama a ensure_models_downloaded y carga los modelos.
    """
    if not ensure_models_downloaded(models_dir):
        raise Exception("No se pudieron descargar los modelos desde GitHub Releases")

    try:
        with open(os.path.join(models_dir, 'similarity_matrix.pkl'), 'rb') as f:
            similarity_matrix = pickle.load(f)

        with open(os.path.join(models_dir, 'scaler.pkl'), 'rb') as f:
            scaler = pickle.load(f)

        df = pd.read_csv(os.path.join(models_dir, 'processed_tracks.csv'))

        return similarity_matrix, scaler, df

    except Exception as e:
        print(f"Error cargando modelos: {e}")
        raise

if __name__ == "__main__":
    print("Descargando modelos desde GitHub Releases (modo local)...")
    ok = ensure_models_downloaded()
    print("Resultado:", ok)
