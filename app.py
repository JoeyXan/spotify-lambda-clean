"""
Sistema de Recomendación de Música - Arquitectura Lambda
Aplicación Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from download_models import load_models
from batch_layer import BatchLayer
from speed_layer import SpeedLayer
from serving_layer import ServingLayer

st.set_page_config(
    page_title="Recomendador de Música - Arquitectura Lambda",
    page_icon="🎵",
    layout="wide"
)

# Inicializar estado de sesión
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.batch = None
    st.session_state.speed = None
    st.session_state.serving = None
    st.session_state.user_id = "usuario_demo"

@st.cache_resource
def load_system():
    """Carga el sistema de recomendación"""
    try:
        similarity_matrix, scaler, df = load_models('models')
        
        batch = BatchLayer()
        batch.load_from_files(similarity_matrix, scaler, df)
        
        speed = SpeedLayer()
        serving = ServingLayer(batch, speed)
        
        return batch, speed, serving
    except Exception as e:
        st.error(f"Error cargando modelos: {e}")
        return None, None, None

# Header
st.title("Recomendador de Música con Arquitectura Lambda")
st.markdown("Sistema híbrido de recomendación basado en datos de Spotify")

# Cargar sistema
with st.spinner('Cargando sistema de recomendación...'):
    batch, speed, serving = load_system()
    
    if batch is None:
        st.error("No se pudo cargar el sistema. Verifica la conexión a internet.")
        st.stop()
    
    st.session_state.batch = batch
    st.session_state.speed = speed
    st.session_state.serving = serving
    st.session_state.initialized = True

# Sidebar
with st.sidebar:
    st.header("Estado del Sistema")
    
    st.metric("Canciones en BD", f"{len(batch.df):,}")
    st.metric("Géneros", f"{batch.df['track_genre'].nunique()}")
    
    st.divider()
    
    st.header("Usuario")
    user_id = st.text_input("ID de Usuario", value=st.session_state.user_id)
    st.session_state.user_id = user_id
    
    recent = speed.get_user_recent_interactions(user_id, limit=3)
    if recent:
        st.subheader("Actividad Reciente")
        for interaction in recent:
            emoji = "▶" if interaction['interaction_type'] == 'play' else "❤" if interaction['interaction_type'] == 'like' else "⏭"
            st.caption(f"{emoji} {interaction['track_name'][:30]}...")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "Recomendaciones",
    "Capa Batch",
    "Capa de Velocidad",
    "Capa de Servicio"
])

# TAB 1: Recomendaciones
with tab1:
    st.header("Obtener Recomendaciones")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input(
            "Buscar canción",
            placeholder="Escribe el nombre de una canción...",
            help="Busca una canción para obtener recomendaciones similares"
        )
        
        if search_query:
            matches = batch.df[
                batch.df['track_name'].str.contains(search_query, case=False, na=False)
            ].head(10)
            
            if not matches.empty:
                st.subheader("Resultados de búsqueda")
                
                selected_track = st.selectbox(
                    "Selecciona una canción:",
                    options=matches.index,
                    format_func=lambda x: f"{matches.loc[x, 'track_name']} - {matches.loc[x, 'artists']} ({matches.loc[x, 'track_genre']})"
                )
                
                if st.button("Obtener Recomendaciones", type="primary"):
                    track_info = matches.loc[selected_track]
                    
                    st.success(f"Canción: {track_info['track_name']} - {track_info['artists']}")
                    
                    serving.update_with_new_interaction(
                        user_id=st.session_state.user_id,
                        track_id=track_info['track_id'],
                        track_name=track_info['track_name'],
                        artists=track_info['artists'],
                        interaction_type='play'
                    )
                    
                    recommendations = serving.get_hybrid_recommendations(
                        track_idx=selected_track,
                        user_id=st.session_state.user_id,
                        top_n=10
                    )
                    
                    st.subheader("Recomendaciones Personalizadas")
                    
                    for idx, rec in recommendations.iterrows():
                        with st.container():
                            col_a, col_b, col_c = st.columns([3, 2, 1])
                            
                            with col_a:
                                st.markdown(f"**{rec['track_name']}**")
                                st.caption(f"{rec['artists']}")
                            
                            with col_b:
                                st.caption(f"Género: {rec['track_genre']}")
                            
                            with col_c:
                                score = rec['similarity_score']
                                st.metric("Similitud", f"{score:.1%}")
                            
                            st.divider()
            else:
                st.warning("No se encontraron canciones con ese nombre.")
    
    with col2:
        st.subheader("Características de Audio")
        st.info("""
        **Características usadas:**
        - Danceability
        - Energy
        - Key & Mode
        - Loudness
        - Speechiness
        - Acousticness
        - Instrumentalness
        - Liveness
        - Valence
        - Tempo
        """)

# TAB 2: Capa Batch
with tab2:
    st.header("Capa Batch - Procesamiento Histórico")
    
    st.markdown("""
    La Capa Batch procesa grandes volúmenes de datos históricos para construir 
    un modelo base de similitud entre canciones usando características de audio de Spotify.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Canciones", f"{len(batch.df):,}")
    
    with col2:
        st.metric("Géneros Únicos", f"{batch.df['track_genre'].nunique()}")
    
    with col3:
        st.metric("Matriz de Similitud", f"{batch.similarity_matrix.shape[0]}x{batch.similarity_matrix.shape[1]}")
    
    st.divider()
    
    st.subheader("Muestra del Dataset")
    
    display_cols = ['track_name', 'artists', 'track_genre', 'popularity', 'danceability', 'energy', 'valence']
    st.dataframe(
        batch.df[display_cols].head(20),
        use_container_width=True,
        hide_index=True
    )
    
    st.subheader("Distribución de Géneros (Top 10)")
    genre_counts = batch.df['track_genre'].value_counts().head(10)
    st.bar_chart(genre_counts)

# TAB 3: Capa de Velocidad
with tab3:
    st.header("Capa de Velocidad - Streaming en Tiempo Real")
    
    st.markdown("""
    La Capa de Velocidad captura y procesa nuevas interacciones de usuarios en tiempo real.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Registrar Nueva Interacción")
        
        random_track = batch.df.sample(1).iloc[0]
        
        st.text_input("Canción", value=random_track['track_name'], disabled=True)
        st.text_input("Artista", value=random_track['artists'], disabled=True)
        
        interaction_type = st.selectbox(
            "Tipo de Interacción",
            options=['play', 'like', 'skip'],
            format_func=lambda x: {'play': 'Reproducir', 'like': 'Me gusta', 'skip': 'Saltar'}[x]
        )
        
        if st.button("Registrar Interacción"):
            serving.update_with_new_interaction(
                user_id=st.session_state.user_id,
                track_id=random_track['track_id'],
                track_name=random_track['track_name'],
                artists=random_track['artists'],
                interaction_type=interaction_type
            )
            st.success(f"Interacción registrada: {interaction_type}")
            st.rerun()
    
    with col2:
        st.subheader("Interacciones Recientes")
        
        recent = speed.get_user_recent_interactions(st.session_state.user_id, limit=10)
        
        if recent:
            for interaction in recent:
                emoji_map = {'play': '▶', 'like': '❤', 'skip': '⏭'}
                emoji = emoji_map.get(interaction['interaction_type'], '♪')
                
                st.markdown(f"""
                **{emoji} {interaction['track_name']}**  
                {interaction['artists']}  
                {interaction['timestamp'][:19]}
                """)
                st.divider()
        else:
            st.info("No hay interacciones registradas aún.")

# TAB 4: Capa de Servicio
with tab4:
    st.header("Capa de Servicio - Fusión de Resultados")
    
    st.markdown("""
    La Capa de Servicio combina los resultados de la Capa Batch y la Capa de Velocidad 
    para generar recomendaciones híbridas y personalizadas.
    """)
    
    st.subheader("Recomendaciones por Características de Audio")
    
    st.markdown("Ajusta las características de audio para encontrar canciones con un mood específico:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        danceability = st.slider("Danceability", 0.0, 1.0, 0.5)
        energy = st.slider("Energy", 0.0, 1.0, 0.5)
        valence = st.slider("Valence (Positividad)", 0.0, 1.0, 0.5)
    
    with col2:
        acousticness = st.slider("Acousticness", 0.0, 1.0, 0.5)
        instrumentalness = st.slider("Instrumentalness", 0.0, 1.0, 0.5)
        speechiness = st.slider("Speechiness", 0.0, 1.0, 0.5)
    
    with col3:
        tempo = st.slider("Tempo (BPM)", 60.0, 200.0, 120.0)
        loudness = st.slider("Loudness (dB)", -20.0, 0.0, -5.0)
    
    if st.button("Buscar Canciones", type="primary"):
        target_features = {
            'danceability': danceability,
            'energy': energy,
            'valence': valence,
            'acousticness': acousticness,
            'instrumentalness': instrumentalness,
            'speechiness': speechiness,
            'tempo': tempo,
            'loudness': loudness,
            'key': 5,
            'mode': 1,
            'liveness': 0.2
        }
        
        recommendations = serving.get_recommendations_by_audio_features(target_features, top_n=10)
        
        st.subheader("Canciones Encontradas")
        
        for idx, rec in recommendations.iterrows():
            col_a, col_b, col_c = st.columns([3, 2, 1])
            
            with col_a:
                st.markdown(f"**{rec['track_name']}**")
                st.caption(f"{rec['artists']}")
            
            with col_b:
                st.caption(f"Género: {rec['track_genre']}")
            
            with col_c:
                st.metric("Match", f"{rec['similarity_score']:.1%}")
            
            st.divider()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem;">
    <p>Sistema de Recomendación de Música - Arquitectura Lambda</p>
    <p>Datos: Spotify Tracks Dataset | Tecnologías: Python, Scikit-learn, Streamlit</p>
</div>
""", unsafe_allow_html=True)
