"""
Capa de Velocidad - Sistema de Recomendación con Arquitectura Lambda
"""

import json
from datetime import datetime
import pandas as pd

class SpeedLayer:
    """
    Capa de Velocidad: Captura eventos en tiempo real
    Funciona en modo simulación sin Redis para Streamlit Cloud
    """
    
    def __init__(self):
        self.interactions = {}
        self.global_stream = []
    
    def add_interaction(self, user_id, track_id, track_name, artists, interaction_type='play'):
        """
        Registra una nueva interacción de usuario
        """
        interaction = {
            'user_id': user_id,
            'track_id': track_id,
            'track_name': track_name,
            'artists': artists,
            'interaction_type': interaction_type,
            'timestamp': datetime.now().isoformat()
        }
        
        if user_id not in self.interactions:
            self.interactions[user_id] = []
        
        self.interactions[user_id].insert(0, interaction)
        self.interactions[user_id] = self.interactions[user_id][:100]
        
        self.global_stream.append(interaction)
        
        return interaction
    
    def get_user_recent_interactions(self, user_id, limit=10):
        """
        Obtiene las interacciones recientes de un usuario
        """
        if user_id not in self.interactions:
            return []
        
        return self.interactions[user_id][:limit]
    
    def get_trending_tracks(self, time_window=3600):
        """
        Obtiene las canciones más populares
        """
        if not self.global_stream:
            return pd.DataFrame()
        
        track_counts = {}
        for event in self.global_stream[-100:]:
            track_id = event.get('track_id')
            if track_id:
                if track_id not in track_counts:
                    track_counts[track_id] = {
                        'track_name': event.get('track_name'),
                        'artists': event.get('artists'),
                        'count': 0
                    }
                track_counts[track_id]['count'] += 1
        
        if not track_counts:
            return pd.DataFrame()
        
        trending = pd.DataFrame.from_dict(track_counts, orient='index')
        trending = trending.sort_values('count', ascending=False)
        return trending
