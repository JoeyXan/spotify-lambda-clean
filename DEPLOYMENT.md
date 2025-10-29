# Guía de Despliegue

## Paso 1: Subir Código a GitHub

### 1.1 Crear repositorio

1. Ve a https://github.com/new
2. Nombre: `spotify-recommender-lambda`
3. Público
4. NO inicializar con README
5. Click en "Create repository"

### 1.2 Subir el código

```bash
cd spotify-lambda-clean
git remote add origin https://github.com/TU-USUARIO/spotify-recommender-lambda.git
git push -u origin main
```

## Paso 2: Subir Modelos a GitHub Releases

Los modelos son muy grandes para el repositorio normal, pero GitHub Releases soporta archivos de hasta 2 GB.

### 2.1 Crear un Release

1. Ve a tu repositorio en GitHub
2. Click en "Releases" (lado derecho)
3. Click en "Create a new release"
4. Tag version: `v1.0`
5. Release title: `Modelos pre-entrenados v1.0`
6. Description: `Modelos del sistema de recomendación`

### 2.2 Subir los archivos

En la sección "Attach binaries", arrastra estos 3 archivos desde `models/`:
- `scaler.pkl`
- `similarity_matrix.pkl`
- `processed_tracks.csv`

Click en "Publish release"

### 2.3 Actualizar download_models.py

Edita el archivo `src/download_models.py` y cambia la línea 13:

```python
GITHUB_USER = "TU-USUARIO"  # Cambiar por tu usuario real de GitHub
```

Por ejemplo, si tu usuario es `juanperez`, debe quedar:

```python
GITHUB_USER = "juanperez"
```

Guarda el cambio y haz commit:

```bash
git add src/download_models.py
git commit -m "Update GitHub user for model downloads"
git push origin main
```

## Paso 3: Desplegar en Streamlit Cloud

### 3.1 Configurar Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Inicia sesión con GitHub
3. Click en "New app"
4. Configuración:
   - Repository: `TU-USUARIO/spotify-recommender-lambda`
   - Branch: `main`
   - Main file path: `app.py`
5. Click en "Deploy!"

### 3.2 Esperar el despliegue

- El despliegue tarda 3-5 minutos
- La app descargará automáticamente los modelos desde GitHub Releases
- Esto solo ocurre en el primer despliegue

### 3.3 Tu link será:

```
https://TU-USUARIO-spotify-recommender-lambda.streamlit.app
```

## Verificación

1. Abre tu link de Streamlit
2. Espera a que cargue (1-2 minutos la primera vez)
3. Verifica que aparezca:
   - "Canciones en BD: 4,832"
   - "Géneros: 114"
4. Prueba buscar una canción

## Troubleshooting

### Error: "No se pudieron descargar los modelos"

Verifica que:
1. Los archivos estén subidos al Release v1.0
2. El Release esté publicado (no en draft)
3. El usuario en `download_models.py` sea correcto

### Error: "404 Not Found"

El Release no existe o el tag es incorrecto. Verifica que el tag sea exactamente `v1.0`

### App muy lenta

Es normal en el primer inicio mientras descarga los modelos (180 MB total).

## Resumen de URLs

- **Repositorio**: `https://github.com/TU-USUARIO/spotify-recommender-lambda`
- **Release**: `https://github.com/TU-USUARIO/spotify-recommender-lambda/releases/tag/v1.0`
- **App**: `https://TU-USUARIO-spotify-recommender-lambda.streamlit.app`
