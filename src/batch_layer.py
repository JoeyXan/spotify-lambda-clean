"""
Capa Batch - Sistema de Recomendación de Música con Arquitectura Lambda
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

class BatchLayer:
    """
    Capa Batch: Procesa datos históricos y genera modelo de similitud
    """
    
    def __init__(self):
        self.df = None
        self.similarity_matrix = None
        self.scaler = StandardScaler()
        self.audio_features = [
            'danceability', 'energy', 'key', 'loudness', 'mode',
            'speechiness', 'acousticness', 'instrumentalness',
            'liveness', 'valence', 'tempo'
        ]
    
    def load_from_files(self, similarity_matrix, scaler, df):
        """
        Carga modelo desde archivos pre-entrenados
        """
        self.similarity_matrix = similarity_matrix
        self.scaler = scaler
        self.df = df
    
    def get_recommendations(self, track_idx, top_n=10):
        """
        Obtiene recomendaciones para una canción
        """
        if self.similarity_matrix is None:
            raise ValueError("Modelo no cargado")
        
        sim_scores = list(enumerate(self.similarity_matrix[track_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]
        track_indices = [i[0] for i in sim_scores]
        
        recommendations = self.df.iloc[track_indices].copy()
        recommendations['similarity_score'] = [i[1] for i in sim_scores]
        
        return recommendations[['track_name', 'artists', 'track_genre', 'similarity_score']]
