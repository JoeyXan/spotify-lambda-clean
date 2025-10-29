# Arquitectura Lambda - Documentación Técnica

## Introducción

La Arquitectura Lambda es un patrón de diseño de procesamiento de datos que combina procesamiento batch y procesamiento en tiempo real para proporcionar vistas completas y actualizadas de los datos.

## Componentes del Sistema

### 1. Capa Batch

**Responsabilidad**: Procesar grandes volúmenes de datos históricos para crear vistas maestras.

**Implementación**:
- Archivo: `src/batch_layer.py`
- Carga del dataset de Spotify (4,832 canciones)
- Extracción de características de audio
- Normalización con StandardScaler
- Cálculo de matriz de similitud coseno

**Características procesadas**:
- danceability (0.0 - 1.0)
- energy (0.0 - 1.0)
- key (0 - 11)
- loudness (dB)
- mode (0 o 1)
- speechiness (0.0 - 1.0)
- acousticness (0.0 - 1.0)
- instrumentalness (0.0 - 1.0)
- liveness (0.0 - 1.0)
- valence (0.0 - 1.0)
- tempo (BPM)

**Algoritmo de similitud**:
```
similarity(A, B) = cos(θ) = (A · B) / (||A|| × ||B||)
```

### 2. Capa de Velocidad

**Responsabilidad**: Capturar y procesar datos en tiempo real.

**Implementación**:
- Archivo: `src/speed_layer.py`
- Captura de interacciones de usuario en tiempo real
- Almacenamiento en memoria
- Mantenimiento de historial reciente por usuario

**Tipos de interacciones**:
- play: Reproducción de canción
- like: Me gusta
- skip: Saltar canción

### 3. Capa de Servicio

**Responsabilidad**: Fusionar resultados de las capas Batch y Velocidad.

**Implementación**:
- Archivo: `src/serving_layer.py`
- Obtener recomendaciones base del modelo batch
- Recuperar historial reciente del usuario
- Aplicar boost personalizado basado en preferencias
- Retornar recomendaciones híbridas ordenadas

**Algoritmo de fusión**:
```python
def hybrid_score(track, user_history):
    base_score = cosine_similarity(track, reference_track)
    
    if track.artist in user_liked_artists:
        boost = 1.2  # 20% de incremento
    else:
        boost = 1.0
    
    final_score = base_score * boost
    
    return final_score
```

## Flujo de Datos

```
Dataset Spotify (114,000 canciones)
         │
         ▼
    CAPA BATCH
    - Carga y muestreo (4,832 canciones)
    - Limpieza de datos
    - Normalización de features
    - Cálculo de similitud coseno
    - Persistencia del modelo
         │
         ▼
  CAPA DE VELOCIDAD
    - Captura de interacciones en tiempo real
    - Almacenamiento en memoria
    - Cálculo de trending tracks
         │
         ▼
   CAPA DE SERVICIO
    - Fusión de resultados batch + velocidad
    - Aplicar boost personalizado
    - Retornar recomendaciones híbridas
         │
         ▼
  INTERFAZ STREAMLIT
    - Búsqueda de canciones
    - Visualización de recomendaciones
    - Registro de interacciones
    - Dashboard de métricas
```

## Ventajas de la Arquitectura Lambda

### 1. Robustez
La capa batch proporciona una vista completa y precisa. Los errores en la capa de velocidad no afectan la vista histórica.

### 2. Baja Latencia
La capa de velocidad procesa eventos en milisegundos. Las consultas se responden con datos actualizados.

### 3. Escalabilidad
- Batch: Se puede procesar en paralelo
- Velocidad: Soporta millones de operaciones/segundo
- Servicio: Stateless, fácil de replicar

### 4. Tolerancia a Fallos
- Datos históricos siempre disponibles (batch)
- Pérdida de datos en velocidad es temporal

## Métricas de Rendimiento

### Capa Batch
- Tiempo de entrenamiento: ~30 segundos (4,832 canciones)
- Tamaño del modelo: ~50 MB
- Tiempo de carga: ~2 segundos

### Capa de Velocidad
- Latencia de escritura: <5 ms
- Latencia de lectura: <2 ms

### Capa de Servicio
- Tiempo de recomendación: <100 ms
- Tiempo con personalización: <150 ms

## Descarga de Modelos

Los modelos pre-entrenados se almacenan en Google Drive y se descargan automáticamente al iniciar la aplicación:

- scaler.pkl: Normalizador de características
- similarity_matrix.pkl: Matriz de similitud (4,832 × 4,832)
- processed_tracks.csv: Dataset procesado

Esto evita problemas con Git LFS y límites de tamaño de archivo en GitHub.
