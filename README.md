# Sistema de Recomendación de Música - Arquitectura Lambda

Sistema híbrido de recomendación de música basado en Arquitectura Lambda, que combina procesamiento batch de datos históricos con streaming en tiempo real para generar recomendaciones personalizadas de canciones de Spotify.

## Descripción del Proyecto

Este proyecto implementa un sistema de recomendación de música utilizando los principios de la Arquitectura Lambda, que consta de tres capas principales:

### Capa Batch
Procesa grandes volúmenes de datos históricos de Spotify para construir un modelo base de similitud entre canciones. Utiliza características de audio como danceability, energy, valence, acousticness, instrumentalness, tempo, key, loudness, entre otras.

**Tecnología**: Scikit-learn para cálculo de similitud coseno sobre características normalizadas.

### Capa de Velocidad
Captura y procesa nuevas interacciones de usuarios en tiempo real (reproducciones, likes, skips).

**Tecnología**: Sistema de almacenamiento en memoria para eventos en tiempo real.

### Capa de Servicio
Fusiona los resultados de las capas Batch y Velocidad para generar recomendaciones híbridas y personalizadas que se actualizan dinámicamente con cada nueva interacción.

## Características Principales

- 4,800+ canciones de 114 géneros diferentes
- Recomendaciones basadas en similitud de características de audio
- Personalización por usuario basada en historial reciente
- Búsqueda por características de audio (mood-based recommendations)
- Interfaz interactiva con Streamlit

## Instalación

### Prerrequisitos

- Python 3.8+
- pip

### Pasos de Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/spotify-recommender-lambda.git
cd spotify-recommender-lambda
```

2. Instalar dependencias
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación descargará automáticamente los modelos pre-entrenados desde Google Drive en la primera ejecución.

## Estructura del Proyecto

```
spotify-recommender-lambda/
│
├── src/
│   ├── batch_layer.py          # Capa Batch
│   ├── speed_layer.py          # Capa de Velocidad
│   ├── serving_layer.py        # Capa de Servicio
│   └── download_models.py      # Descarga de modelos desde Google Drive
│
├── models/                      # Modelos (se descargan automáticamente)
│
├── app.py                       # Aplicación Streamlit
├── requirements.txt             # Dependencias
└── README.md                    # Este archivo
```

## Uso de la Aplicación

### 1. Búsqueda de Recomendaciones

- Ingresa el nombre de una canción en el buscador
- Selecciona la canción deseada de los resultados
- Haz clic en "Obtener Recomendaciones"
- Visualiza las 10 canciones más similares con sus scores de similitud

### 2. Registro de Interacciones

- Ve a la pestaña "Capa de Velocidad"
- Selecciona el tipo de interacción (play, like, skip)
- Registra la interacción para actualizar tus preferencias

### 3. Búsqueda por Características de Audio

- Ve a la pestaña "Capa de Servicio"
- Ajusta los sliders de características (danceability, energy, valence, etc.)
- Encuentra canciones que coincidan con el mood deseado

## Arquitectura Técnica

### Flujo de Datos

```
Dataset Spotify (114K canciones)
         │
         ▼
    CAPA BATCH
    - Carga de datos
    - Normalización features
    - Cálculo similitud coseno
    - Modelo base persistente
         │
         ▼
  CAPA DE VELOCIDAD
    - Captura interacciones
    - Almacenamiento en memoria
    - Trending en tiempo real
         │
         ▼
   CAPA DE SERVICIO
    - Fusión batch + velocidad
    - Personalización usuario
    - Recomendaciones híbridas
```

### Algoritmo de Recomendación

1. Extracción de características: Se utilizan 11 características de audio de Spotify
2. Normalización: StandardScaler para normalizar features
3. Similitud coseno: Cálculo de matriz de similitud entre todas las canciones
4. Boost personalizado: Ajuste de scores basado en historial del usuario
5. Ranking final: Ordenamiento por score de similitud ajustado

## Dataset

**Fuente**: Spotify Tracks Dataset - Kaggle

**Características**:
- 114,000 canciones
- 125 géneros musicales
- 21 columnas de información por canción
- Características de audio oficiales de Spotify Web API

**Características de Audio Utilizadas**:
- danceability: Qué tan bailable es la canción (0.0 - 1.0)
- energy: Intensidad y actividad (0.0 - 1.0)
- key: Tonalidad musical (0-11)
- loudness: Volumen en decibelios
- mode: Modalidad (mayor/menor)
- speechiness: Presencia de palabras habladas (0.0 - 1.0)
- acousticness: Confianza de que es acústica (0.0 - 1.0)
- instrumentalness: Predicción de contenido vocal (0.0 - 1.0)
- liveness: Presencia de audiencia (0.0 - 1.0)
- valence: Positividad musical (0.0 - 1.0)
- tempo: Velocidad en BPM

## Tecnologías Utilizadas

- Python 3.11
- Pandas: Manipulación de datos
- NumPy: Operaciones numéricas
- Scikit-learn: Machine Learning (similitud coseno, normalización)
- Streamlit: Framework de interfaz web
- Requests: Descarga de modelos desde Google Drive

## Despliegue en Streamlit Cloud

1. Sube tu código a GitHub
2. Ve a https://share.streamlit.io/
3. Inicia sesión con GitHub
4. Click en "New app"
5. Selecciona tu repositorio
6. Main file: app.py
7. Click en "Deploy"

Los modelos se descargarán automáticamente desde Google Drive en el primer despliegue.

## Licencia

Este proyecto utiliza el dataset de Spotify bajo licencia ODbL-1.0 (Open Database License).

## Autor

Desarrollado como proyecto educativo de Arquitectura Lambda aplicada a sistemas de recomendación.
