"""
Modulo per il tracking dei movimenti usando MediaPipe
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Dict, Tuple
import time

class MotionTracker:
    """Classe per tracciare i movimenti dell'utente usando MediaPipe Pose"""
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Inizializza il motion tracker
        
        Args:
            camera_index: Indice della videocamera
            width: Larghezza del frame
            height: Altezza del frame
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        
        # Inizializza MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )
        
        # Inizializza la videocamera
        self.cap = None
        self.last_positions = {}  # Per calcolare la velocità
        self.last_time = time.time()
        
        # Filtro per smoothing delle posizioni
        self.position_history = {}  # Storia delle posizioni per smoothing
        self.history_size = 5
        
    def initialize_camera(self) -> bool:
        """Inizializza la videocamera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            return self.cap.isOpened()
        except Exception as e:
            print(f"Errore nell'inizializzazione della videocamera: {e}")
            return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Ottiene un frame dalla videocamera"""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return cv2.flip(frame, 1)  # Specchia il frame per effetto specchio
    
    def detect_pose(self, frame: np.ndarray) -> Optional[Dict]:
        """
        Rileva la posa dell'utente nel frame
        
        Returns:
            Dizionario con le posizioni delle articolazioni chiave
        """
        if frame is None:
            return None
        
        # Converti BGR a RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        
        # Processa il frame
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return None
        
        # Estrai le posizioni delle articolazioni chiave
        landmarks = results.pose_landmarks.landmark
        
        # Converti in coordinate normalizzate (0-1) con smoothing
        raw_key_points = {
            'left_wrist': np.array([
                landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].x,
                landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].y,
                landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].z
            ]),
            'right_wrist': np.array([
                landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].x,
                landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y,
                landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].z
            ]),
            'left_knee': np.array([
                landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].x,
                landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].y,
                landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].z
            ]),
            'right_knee': np.array([
                landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].x,
                landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].y,
                landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].z
            ]),
            'left_ankle': np.array([
                landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].x,
                landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].y,
                landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].z
            ]),
            'right_ankle': np.array([
                landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].x,
                landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].y,
                landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].z
            ]),
            'nose': np.array([
                landmarks[self.mp_pose.PoseLandmark.NOSE].x,
                landmarks[self.mp_pose.PoseLandmark.NOSE].y,
                landmarks[self.mp_pose.PoseLandmark.NOSE].z
            ])
        }
        
        # Applica smoothing
        key_points = {}
        for point_name, point in raw_key_points.items():
            if point_name not in self.position_history:
                self.position_history[point_name] = []
            
            self.position_history[point_name].append(point)
            if len(self.position_history[point_name]) > self.history_size:
                self.position_history[point_name].pop(0)
            
            # Media mobile per smoothing
            if len(self.position_history[point_name]) > 1:
                smoothed = np.mean(self.position_history[point_name], axis=0)
                key_points[point_name] = smoothed
            else:
                key_points[point_name] = point
        
        return {
            'key_points': key_points,
            'landmarks': results.pose_landmarks,
            'frame': frame
        }
    
    def calculate_velocity(self, current_pos: np.ndarray, last_pos: np.ndarray, dt: float) -> float:
        """Calcola la velocità di movimento"""
        if dt == 0:
            return 0.0
        
        distance = np.linalg.norm(current_pos - last_pos)
        velocity = distance / dt
        return velocity
    
    def get_hand_velocities(self, key_points: Dict) -> Dict[str, float]:
        """
        Calcola le velocità delle mani
        
        Returns:
            Dizionario con velocità di left_wrist e right_wrist
        """
        current_time = time.time()
        dt = current_time - self.last_time
        
        velocities = {}
        
        for hand in ['left_wrist', 'right_wrist']:
            if hand in key_points:
                current_pos = key_points[hand]
                
                if hand in self.last_positions:
                    last_pos = self.last_positions[hand]
                    velocities[hand] = self.calculate_velocity(current_pos, last_pos, dt)
                else:
                    velocities[hand] = 0.0
                
                self.last_positions[hand] = current_pos
        
        self.last_time = current_time
        return velocities
    
    def draw_pose(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """Disegna la posa sul frame"""
        if landmarks is None:
            return frame
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.mp_drawing.draw_landmarks(
            rgb_frame,
            landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        
        return cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
    
    def release(self):
        """Rilascia le risorse"""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

