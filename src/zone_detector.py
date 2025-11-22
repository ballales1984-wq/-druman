"""
Modulo per rilevare quando l'utente colpisce una zona della batteria
"""
import numpy as np
from typing import Dict, Optional, Set, Tuple
import sys
import os

# Aggiungi il percorso del progetto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DRUM_ZONES, VELOCITY_THRESHOLD

class ZoneDetector:
    """Classe per rilevare i colpi sulle zone della batteria"""
    
    def __init__(self):
        """Inizializza il rilevatore di zone"""
        self.drum_zones = DRUM_ZONES
        self.velocity_threshold = VELOCITY_THRESHOLD
        
        # Traccia le posizioni precedenti per calcolare la velocità
        self.previous_positions = {}
    
    def distance_to_zone(self, point: np.ndarray, zone_center: np.ndarray) -> float:
        """Calcola la distanza euclidea da un punto a una zona"""
        return np.linalg.norm(point - zone_center)
    
    def is_point_in_zone(self, point: np.ndarray, zone_config: Dict) -> bool:
        """
        Verifica se un punto è all'interno della zona di trigger
        Supporta diversi tipi di rilevamento:
        - horizontal: usa X (sinistra/destra) e Y (altezza)
        - knee: usa ginocchio/gamba (X e Y)
        - height_range: solo altezza Y (retrocompatibilità)
        
        Args:
            point: Punto 3D normalizzato [x, y, z]
            zone_config: Configurazione della zona
        
        Returns:
            True se il punto è nella zona
        """
        position_type = zone_config.get('position_type', 'height_range')
        
        # Rilevamento orizzontale (sinistra/destra) per hi-hat e snare
        if position_type == 'horizontal':
            if 'x_range' in zone_config and 'y_range' in zone_config:
                x_min, x_max = zone_config['x_range']
                y_min, y_max = zone_config['y_range']
                x = point[0]  # Coordinata X normalizzata (0-1)
                y = point[1]  # Coordinata Y normalizzata (0-1)
                return (x_min <= x <= x_max) and (y_min <= y <= y_max)
        
        # Rilevamento ginocchio/gamba per kick
        elif position_type == 'knee':
            if 'x_range' in zone_config and 'y_range' in zone_config:
                x_min, x_max = zone_config['x_range']
                y_min, y_max = zone_config['y_range']
                x = point[0]
                y = point[1]
                return (x_min <= x <= x_max) and (y_min <= y <= y_max)
        
        # Retrocompatibilità: solo altezza Y
        elif 'height_range' in zone_config:
            y_min, y_max = zone_config['height_range']
            y = point[1]
            return y_min <= y <= y_max
        
        # Fallback: distanza euclidea tradizionale
        distance = self.distance_to_zone(point, zone_config['center'])
        return distance <= zone_config['trigger_distance']
    
    def detect_hits(self, key_points: Dict, velocities: Dict) -> Set[str]:
        """
        Rileva quali zone sono state colpite
        Configurazione per batterista SEDUTO:
        - Hi-Hat a DESTRA (mano destra)
        - Snare a SINISTRA (mano sinistra)
        - Kick con ginocchio/gamba
        
        Args:
            key_points: Punti chiave dell'utente (coordinate normalizzate)
            velocities: Velocità dei movimenti
        
        Returns:
            Set di nomi delle zone colpite
        """
        hit_zones = set()
        
        # Controlla mano DESTRA per Snare (INVERTITO)
        if 'right_wrist' in key_points:
            point = key_points['right_wrist']
            velocity = velocities.get('right_wrist', 0.0)
            
            if velocity >= self.velocity_threshold:
                if 'snare' in self.drum_zones and self.is_point_in_zone(point, self.drum_zones['snare']):
                    hit_zones.add('snare')
        
        # Controlla mano SINISTRA per Hi-Hat (INVERTITO)
        if 'left_wrist' in key_points:
            point = key_points['left_wrist']
            velocity = velocities.get('left_wrist', 0.0)
            
            if velocity >= self.velocity_threshold:
                if 'hihat' in self.drum_zones and self.is_point_in_zone(point, self.drum_zones['hihat']):
                    hit_zones.add('hihat')
        
        # Controlla GINOCCHIA/GAMBE per Kick
        for knee in ['left_knee', 'right_knee']:
            if knee in key_points:
                point = key_points[knee]
                velocity = velocities.get(knee, 0.0)
                
                if velocity >= self.velocity_threshold:
                    if 'kick' in self.drum_zones and self.is_point_in_zone(point, self.drum_zones['kick']):
                        hit_zones.add('kick')
                        break  # Un ginocchio alla volta
        
        # Fallback: usa anche caviglie se ginocchia non disponibili
        if 'kick' not in hit_zones:
            for ankle in ['left_ankle', 'right_ankle']:
                if ankle in key_points:
                    point = key_points[ankle]
                    velocity = velocities.get(ankle, 0.0)
                    
                    if velocity >= self.velocity_threshold:
                        if 'kick' in self.drum_zones and self.is_point_in_zone(point, self.drum_zones['kick']):
                            hit_zones.add('kick')
                            break
        
        return hit_zones
    
    def get_zone_velocity(self, point: np.ndarray, zone_config: Dict) -> float:
        """
        Calcola la velocità relativa a una zona (per intensità del suono)
        
        Args:
            point: Punto 3D
            zone_config: Configurazione della zona
        
        Returns:
            Velocità normalizzata (0-1)
        """
        distance = self.distance_to_zone(point, zone_config['center'])
        max_distance = zone_config['trigger_distance']
        
        if distance > max_distance:
            return 0.0
        
        # Velocità inversamente proporzionale alla distanza
        normalized_distance = distance / max_distance
        velocity = 1.0 - normalized_distance
        
        return np.clip(velocity, 0.0, 1.0)

