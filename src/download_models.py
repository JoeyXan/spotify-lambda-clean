"""
Módulo para descargar modelos desde GitHub Releases
"""

import os
import requests
import pickle
import pandas as pd
from pathlib import Path

# URL base de GitHub Releases
# Actualizar con tu usuario de GitHub después de subir los archivos
GITHUB_USER = "JoeyXan"  # Cambiar por tu usuario de GitHub
GITHUB_REPO = "spotify-recommender-lambda"
RELEASE_TAG = "v1.0"

# Archivos a descargar
MODEL_FILES = {
    'scaler.pkl': f'https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/scaler.pkl',
    'similarity_matrix.pkl': f'https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/similarity_matrix.pkl',
    'processed_tracks.csv': f'https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/processed_tracks.csv'
}

def download_file(url, destination):
    """
    Descarga un archivo desde una URL
    """
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"  Progreso: {percent:.1f}%", end='\r')
        
        print(f"  Completado")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def ensure_models_downloaded(models_dir='models'):
    """
    Verifica y descarga los modelos si no existen
    """
    Path(models_dir).mkdir(parents=True, exist_ok=True)
    
    for filename, url in MODEL_FILES.items():
        filepath = os.path.join(models_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Descargando {filename}...")
            
            if not download_file(url, filepath):
                print(f"Error descargando {filename}")
                return False
            
            # Verificar tamaño
            if os.path.getsize(filepath) < 1000 and filename.endswith('.pkl'):
                print(f"Error: {filename} parece estar corrupto")
                os.remove(filepath)
                return False
    
    return True

def load_models(models_dir='models'):
    """
    Carga los modelos desde el directorio
    """
    # Asegurar que los modelos estén descargados
    if not ensure_models_downloaded(models_dir):
        raise Exception("No se pudieron descargar los modelos desde GitHub Releases")
    
    # Cargar archivos
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
    print("Descargando modelos desde GitHub Releases...")
    if ensure_models_downloaded():
        print("Modelos descargados correctamente")
    else:
        print("Error en la descarga")
