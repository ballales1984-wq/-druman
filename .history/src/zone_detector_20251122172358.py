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
        Per i pad in colonna, controlla solo l'altezza (Y), ignora X
        
        Args:
            point: Punto 3D normalizzato [x, y, z]
            zone_config: Configurazione della zona
        
        Returns:
            True se il punto è nella zona
        """
        # Se c'è un height_range, usa solo l'altezza Y (ignora X)
        if 'height_range' in zone_config:
            y_min, y_max = zone_config['height_range']
            y = point[1]  # Coordinata Y normalizzata (0-1)
            # Controlla solo se Y è nel range, X può essere ovunque
            return y_min <= y <= y_max
        
        # Fallback: distanza euclidea tradizionale (per retrocompatibilità)
        distance = self.distance_to_zone(point, zone_config['center'])
        return distance <= zone_config['trigger_distance']
    
    def detect_hits(self, key_points: Dict, velocities: Dict) -> Set[str]:
        """
        Rileva quali zone sono state colpite
        Basato sull'ALTEZZA delle mani (coordinata Y)
        
        Args:
            key_points: Punti chiave dell'utente (coordinate normalizzate)
            velocities: Velocità dei movimenti
        
        Returns:
            Set di nomi delle zone colpite
        """
        hit_zones = set()
        
        # Controlla i polsi (mani) per i colpi - basato su ALTEZZA
        for hand in ['left_wrist', 'right_wrist']:
            if hand not in key_points:
                continue
            
            point = key_points[hand]
            velocity = velocities.get(hand, 0.0)
            
            # Verifica se la velocità è sufficiente per un colpo
            if velocity < self.velocity_threshold:
                continue
            
            # Controlla tutte le zone (escluso kick che è per i piedi)
            for zone_name, zone_config in self.drum_zones.items():
                if zone_name == 'kick':
                    continue  # Skip kick per le mani
                
                if self.is_point_in_zone(point, zone_config):
                    hit_zones.add(zone_name)
                    break  # Una mano può colpire solo una zona alla volta
        
        # Controlla i piedi (caviglie) per il kick - solo altezza
        for foot in ['left_ankle', 'right_ankle']:
            if foot not in key_points:
                continue
            
            point = key_points[foot]
            velocity = velocities.get(foot, 0.0)
            
            # Per il kick, controlla solo la zona kick (basato su altezza)
            if velocity >= self.velocity_threshold:
                if self.is_point_in_zone(point, self.drum_zones['kick']):
                    hit_zones.add('kick')
        
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

