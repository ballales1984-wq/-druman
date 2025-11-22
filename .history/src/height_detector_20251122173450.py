"""
Sistema di rilevamento automatico dell'altezza delle mani
Calcola dinamicamente le posizioni dei pad basandosi sull'altezza reale dell'utente
"""
import numpy as np
from typing import Dict, Optional, Tuple, List
from collections import deque
import time

class HeightDetector:
    """Rileva automaticamente l'altezza delle mani e posiziona i pad dinamicamente"""
    
    def __init__(self, num_pads: int = 6):
        """
        Inizializza il detector di altezza
        
        Args:
            num_pads: Numero di pad da posizionare (default: 6)
        """
        self.num_pads = num_pads
        
        # Buffer per tracciare altezze delle mani
        self.hand_heights = deque(maxlen=100)  # Ultimi 100 frame
        self.foot_heights = deque(maxlen=100)
        
        # Range di altezza rilevato
        self.min_hand_height = None
        self.max_hand_height = None
        self.min_foot_height = None
        self.max_foot_height = None
        
        # Stato calibrazione
        self.calibrated = False
        self.calibration_samples = 0
        self.calibration_duration = 3.0  # Secondi di calibrazione
        self.calibration_start_time = None
        
        # Pad positions (calcolate dinamicamente)
        self.pad_positions = {}
        
        # Statistiche
        self.stats = {
            'calibration_frames': 0,
            'hand_detections': 0,
            'foot_detections': 0
        }
    
    def add_hand_height(self, y: float):
        """
        Aggiunge un'altezza di mano al buffer
        
        Args:
            y: Coordinata Y normalizzata (0-1)
        """
        if 0 <= y <= 1:
            self.hand_heights.append(y)
            self.stats['hand_detections'] += 1
    
    def add_foot_height(self, y: float):
        """
        Aggiunge un'altezza di piede al buffer
        
        Args:
            y: Coordinata Y normalizzata (0-1)
        """
        if 0 <= y <= 1:
            self.foot_heights.append(y)
            self.stats['foot_detections'] += 1
    
    def start_calibration(self):
        """Inizia la calibrazione automatica"""
        self.calibrated = False
        self.calibration_samples = 0
        self.calibration_start_time = time.time()
        self.hand_heights.clear()
        self.foot_heights.clear()
        print("[INFO] Calibrazione altezza iniziata - muovi le mani dall'alto al basso per 3 secondi")
    
    def update_calibration(self, key_points: Dict):
        """
        Aggiorna la calibrazione con nuovi keypoints
        
        Args:
            key_points: Punti chiave MediaPipe
        """
        if self.calibration_start_time is None:
            return
        
        # Raccogli altezze delle mani
        for hand in ['left_wrist', 'right_wrist']:
            if hand in key_points:
                y = key_points[hand][1]  # Coordinata Y
                self.add_hand_height(y)
        
        # Raccogli altezze dei piedi
        for foot in ['left_ankle', 'right_ankle']:
            if foot in key_points:
                y = key_points[foot][1]  # Coordinata Y
                self.add_foot_height(y)
        
        self.calibration_samples += 1
        self.stats['calibration_frames'] += 1
        
        # Verifica se calibrazione completata
        elapsed = time.time() - self.calibration_start_time
        if elapsed >= self.calibration_duration and len(self.hand_heights) > 20:
            self.finish_calibration()
    
    def finish_calibration(self):
        """Completa la calibrazione e calcola posizioni pad"""
        if len(self.hand_heights) < 10:
            print("[WARN] Pochi campioni per calibrazione, uso posizioni default")
            self._use_default_positions()
            return
        
        # Calcola range altezza mani
        hand_heights_array = np.array(list(self.hand_heights))
        self.min_hand_height = np.percentile(hand_heights_array, 5)  # 5° percentile (estremo alto)
        self.max_hand_height = np.percentile(hand_heights_array, 95)  # 95° percentile (estremo basso)
        
        # Calcola range altezza piedi
        if len(self.foot_heights) > 10:
            foot_heights_array = np.array(list(self.foot_heights))
            self.min_foot_height = np.percentile(foot_heights_array, 10)
            self.max_foot_height = np.percentile(foot_heights_array, 90)
        else:
            # Stima basata su mani
            self.min_foot_height = self.max_hand_height + 0.1
            self.max_foot_height = min(1.0, self.max_hand_height + 0.3)
        
        # Calcola posizioni pad dinamicamente
        self._calculate_pad_positions()
        
        self.calibrated = True
        self.calibration_start_time = None
        
        print(f"[OK] Calibrazione completata!")
        print(f"  Range mani: {self.min_hand_height:.2f} - {self.max_hand_height:.2f}")
        print(f"  Range piedi: {self.min_foot_height:.2f} - {self.max_foot_height:.2f}")
        print(f"  Pad posizionati dinamicamente")
    
    def _calculate_pad_positions(self):
        """Calcola posizioni pad basandosi sui range rilevati - SENZA SOVRAPPOSIZIONI"""
        # Pad per le mani (5 pad: crash, hihat, tom2, snare, tom1)
        hand_range = self.max_hand_height - self.min_hand_height
        hand_start = self.min_hand_height
        
        # Dividi lo spazio delle mani in 5 zone SENZA SOVRAPPOSIZIONI
        hand_pads = ['crash', 'hihat', 'tom2', 'snare', 'tom1']
        num_hand_pads = len(hand_pads)
        
        # Calcola range per ogni pad senza sovrapposizioni
        # Ogni pad occupa una porzione dello spazio totale
        range_per_pad = hand_range / num_hand_pads
        
        for i, pad_name in enumerate(hand_pads):
            # Calcola il range per questo pad (senza sovrapposizioni)
            y_min = hand_start + (range_per_pad * i)
            y_max = hand_start + (range_per_pad * (i + 1))
            
            # Posizione centrale del pad
            y_center = (y_min + y_max) / 2
            
            # Aggiungi un piccolo margine interno per evitare attivazioni accidentali ai bordi
            margin = range_per_pad * 0.1  # 10% di margine
            y_min += margin
            y_max -= margin
            
            # Assicura che non esca dai limiti
            y_min = max(0.0, y_min)
            y_max = min(1.0, y_max)
            
            # Assicura che y_min < y_max
            if y_min >= y_max:
                y_max = y_min + 0.05  # Almeno 5% di range
            
            self.pad_positions[pad_name] = {
                'center': np.array([0.5, y_center, 0.0]),
                'height_range': (y_min, y_max),
                'radius': range_per_pad * 0.3,
                'trigger_distance': range_per_pad * 0.5
            }
        
        # Pad per i piedi (kick)
        foot_range = self.max_foot_height - self.min_foot_height
        foot_center = (self.min_foot_height + self.max_foot_height) / 2
        
        self.pad_positions['kick'] = {
            'center': np.array([0.5, foot_center, 0.0]),
            'height_range': (self.min_foot_height, self.max_foot_height),
            'radius': foot_range * 0.3
        }
    
    def _use_default_positions(self):
        """Usa posizioni default se calibrazione fallisce"""
        default_positions = {
            'crash': {'center': np.array([0.5, 0.15, 0.0]), 'height_range': (0.0, 0.25), 'radius': 0.10},
            'hihat': {'center': np.array([0.5, 0.30, 0.0]), 'height_range': (0.20, 0.40), 'radius': 0.10},
            'tom2': {'center': np.array([0.5, 0.50, 0.0]), 'height_range': (0.40, 0.60), 'radius': 0.10},
            'snare': {'center': np.array([0.5, 0.70, 0.0]), 'height_range': (0.60, 0.80), 'radius': 0.12},
            'tom1': {'center': np.array([0.5, 0.85, 0.0]), 'height_range': (0.75, 0.95), 'radius': 0.10},
            'kick': {'center': np.array([0.5, 0.95, 0.0]), 'height_range': (0.85, 1.0), 'radius': 0.15}
        }
        self.pad_positions = default_positions
        self.calibrated = True
    
    def get_pad_positions(self) -> Dict:
        """
        Restituisce le posizioni dei pad calcolate
        
        Returns:
            Dizionario con posizioni pad
        """
        if not self.calibrated:
            return {}
        return self.pad_positions.copy()
    
    def is_calibrated(self) -> bool:
        """Verifica se la calibrazione è completata"""
        return self.calibrated
    
    def get_calibration_progress(self) -> float:
        """
        Restituisce il progresso della calibrazione (0-1)
        
        Returns:
            Progresso calibrazione
        """
        if self.calibration_start_time is None:
            return 1.0 if self.calibrated else 0.0
        
        elapsed = time.time() - self.calibration_start_time
        return min(1.0, elapsed / self.calibration_duration)
    
    def get_statistics(self) -> Dict:
        """Restituisce statistiche"""
        return {
            'calibrated': self.calibrated,
            'calibration_progress': self.get_calibration_progress(),
            'hand_range': (self.min_hand_height, self.max_hand_height) if self.calibrated else None,
            'foot_range': (self.min_foot_height, self.max_foot_height) if self.calibrated else None,
            'stats': self.stats.copy()
        }

