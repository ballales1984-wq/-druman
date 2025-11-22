"""
Modulo per la calibrazione del sistema
"""
import numpy as np
import cv2
import time
from typing import Dict, Optional, Tuple
from src.motion_tracker import MotionTracker
from src.config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT

class CalibrationSystem:
    """Sistema di calibrazione per posizionare l'utente nello spazio"""
    
    def __init__(self, motion_tracker: MotionTracker):
        """
        Inizializza il sistema di calibrazione
        
        Args:
            motion_tracker: Istanza del motion tracker
        """
        self.motion_tracker = motion_tracker
        self.calibration_points = {}
        self.calibration_complete = False
        
        # Punti di riferimento per la calibrazione
        self.reference_points = {
            'center': None,      # Centro del corpo (petto)
            'left_extreme': None,  # Estremo sinistro
            'right_extreme': None, # Estremo destro
            'top': None,          # Punto più alto
            'bottom': None        # Punto più basso
        }
    
    def calibrate(self, duration: float = 5.0) -> bool:
        """
        Esegue la calibrazione automatica
        
        Args:
            duration: Durata della calibrazione in secondi
        
        Returns:
            True se la calibrazione è riuscita
        """
        print("=" * 50)
        print("CALIBRAZIONE")
        print("=" * 50)
        print("Posizionati davanti alla camera")
        print("Muoviti naturalmente per 5 secondi...")
        print("=" * 50)
        
        positions = {
            'left_wrist': [],
            'right_wrist': [],
            'left_ankle': [],
            'right_ankle': [],
            'nose': []
        }
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            frame = self.motion_tracker.get_frame()
            if frame is None:
                continue
            
            pose_data = self.motion_tracker.detect_pose(frame)
            
            if pose_data:
                key_points = pose_data['key_points']
                
                for point_name in positions.keys():
                    if point_name in key_points:
                        positions[point_name].append(key_points[point_name].copy())
            
            frame_count += 1
            elapsed = time.time() - start_time
            if frame_count % 10 == 0:
                print(f"Calibrazione... {elapsed:.1f}s / {duration:.1f}s", end='\r')
        
        print("\nElaborazione dati calibrazione...")
        
        # Calcola i range di movimento
        self.calibration_points = {}
        for point_name, point_list in positions.items():
            if len(point_list) > 10:  # Almeno 10 campioni
                points_array = np.array(point_list)
                self.calibration_points[point_name] = {
                    'min': np.min(points_array, axis=0),
                    'max': np.max(points_array, axis=0),
                    'center': np.mean(points_array, axis=0),
                    'std': np.std(points_array, axis=0)
                }
        
        # Verifica che abbiamo abbastanza dati
        if len(self.calibration_points) >= 3:
            self.calibration_complete = True
            print("✓ Calibrazione completata con successo!")
            print(f"  Punti calibrati: {len(self.calibration_points)}")
            return True
        else:
            print("✗ Calibrazione fallita: dati insufficienti")
            print("  Assicurati di essere visibile nella camera e muoviti di più")
            return False
    
    def normalize_position(self, point: np.ndarray, point_type: str = 'wrist') -> np.ndarray:
        """
        Normalizza una posizione basandosi sulla calibrazione
        
        Args:
            point: Punto 3D da normalizzare
            point_type: Tipo di punto ('wrist', 'ankle', 'nose')
        
        Returns:
            Punto normalizzato nello spazio della batteria
        """
        if not self.calibration_complete:
            return point  # Restituisce il punto originale se non calibrato
        
        # Trova il punto di calibrazione più appropriato
        calib_key = None
        if point_type == 'wrist':
            # Usa la media dei polsi
            if 'left_wrist' in self.calibration_points and 'right_wrist' in self.calibration_points:
                left_center = self.calibration_points['left_wrist']['center']
                right_center = self.calibration_points['right_wrist']['center']
                calib_center = (left_center + right_center) / 2
                calib_min = np.minimum(
                    self.calibration_points['left_wrist']['min'],
                    self.calibration_points['right_wrist']['min']
                )
                calib_max = np.maximum(
                    self.calibration_points['left_wrist']['max'],
                    self.calibration_points['right_wrist']['max']
                )
            else:
                return point
        elif point_type == 'ankle':
            if 'left_ankle' in self.calibration_points:
                calib_center = self.calibration_points['left_ankle']['center']
                calib_min = self.calibration_points['left_ankle']['min']
                calib_max = self.calibration_points['left_ankle']['max']
            else:
                return point
        else:
            return point
        
        # Normalizza rispetto al range di calibrazione
        range_size = calib_max - calib_min
        range_size = np.where(range_size < 0.01, 0.01, range_size)  # Evita divisione per zero
        
        normalized = (point - calib_min) / range_size
        
        # Centra e scala per lo spazio della batteria
        # X: 0.2 - 0.8 (lati)
        # Y: 0.3 - 0.7 (alto-basso)
        # Z: mantieni originale
        normalized[0] = 0.2 + normalized[0] * 0.6  # X
        normalized[1] = 0.3 + normalized[1] * 0.4  # Y
        # normalized[2] rimane invariato
        
        return normalized
    
    def get_calibration_info(self) -> Dict:
        """Restituisce informazioni sulla calibrazione"""
        return {
            'complete': self.calibration_complete,
            'points': len(self.calibration_points),
            'details': self.calibration_points
        }

