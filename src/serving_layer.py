"""
Capa de Servicio - Sistema de Recomendación con Arquitectura Lambda
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ServingLayer:
    """
    Capa de Servicio: Fusiona resultados de batch y velocidad
    """
    
    def __init__(self, batch_layer, speed_layer):
        self.batch = batch_layer
        self.speed = speed_layer
        self.audio_features = [
            'danceability', 'energy', 'key', 'loudness', 'mode',
            'speechiness', 'acousticness', 'instrumentalness',
            'liveness', 'valence', 'tempo'
        ]
    
    def get_hybrid_recommendations(self, track_idx, user_id=None, top_n=10):
        """
        Genera recomendaciones híbridas
        """
        batch_recs = self.batch.get_recommendations(track_idx, top_n=top_n*2)
        
        if user_id:
            recent_interactions = self.speed.get_user_recent_interactions(user_id, limit=20)
            
            if recent_interactions:
                liked_tracks = [i for i in recent_interactions if i['interaction_type'] == 'like']
                
                if liked_tracks:
                    batch_recs = self._apply_user_preferences(batch_recs, liked_tracks)
        
        return batch_recs.head(top_n)
    
    def _apply_user_preferences(self, recommendations, liked_tracks):
        """
        Ajusta scores basado en preferencias del usuario
        """
        liked_artists = set()
        for track in liked_tracks:
            artists = track.get('artists', '').split(';')
            liked_artists.update([a.strip() for a in artists])
        
        def boost_score(row):
            artists = str(row['artists']).split(';')
            artists = [a.strip() for a in artists]
            
            if any(artist in liked_artists for artist in artists):
                return row['similarity_score'] * 1.2
            return row['similarity_score']
        
        recommendations['similarity_score'] = recommendations.apply(boost_score, axis=1)
        recommendations = recommendations.sort_values('similarity_score', ascending=False)
        
        return recommendations
    
    def get_personalized_recommendations_by_name(self, track_name, user_id=None, top_n=10):
        """
        Obtiene recomendaciones buscando por nombre de canción
        """
        matches = self.batch.df[
            self.batch.df['track_name'].str.contains(track_name, case=False, na=False)
        ]
        
        if matches.empty:
            return pd.DataFrame(), None
        
        track_idx = matches.index[0]
        track_info = matches.iloc[0]
        
        recommendations = self.get_hybrid_recommendations(track_idx, user_id, top_n)
        
        return recommendations, track_info
    
    def get_recommendations_by_audio_features(self, target_features, top_n=10):
        """
        Genera recomendaciones basadas en características de audio
        """
        feature_vector = np.array([
            target_features.get(feat, 0.5) for feat in self.audio_features
        ]).reshape(1, -1)
        
        feature_vector_scaled = self.batch.scaler.transform(feature_vector)
        
        dataset_features = self.batch.scaler.transform(
            self.batch.df[self.audio_features]
        )
        
        similarities = cosine_similarity(feature_vector_scaled, dataset_features)[0]
        
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        recommendations = self.batch.df.iloc[top_indices].copy()
        recommendations['similarity_score'] = similarities[top_indices]
        
        return recommendations[['track_name', 'artists', 'track_genre', 'similarity_score']]
    
    def update_with_new_interaction(self, user_id, track_id, track_name, artists, interaction_type='play'):
        """
        Registra una nueva interacción
        """
        return self.speed.add_interaction(
            user_id, track_id, track_name, artists, interaction_type
        )
