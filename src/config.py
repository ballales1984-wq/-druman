"""
Configurazioni per DrumMan
"""
import numpy as np

# Configurazione Camera
CAMERA_INDEX = 0  # Indice della videocamera (0 = default)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FPS = 30

# Configurazione Motion Tracking
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# Configurazione Zone Batteria Virtuale
# Coordinate normalizzate (0-1) nello spazio 3D
DRUM_ZONES = {
    'kick': {
        'center': np.array([0.5, 0.7, 0.0]),  # x, y, z
        'radius': 0.15,
        'trigger_distance': 0.2
    },
    'snare': {
        'center': np.array([0.5, 0.5, 0.0]),
        'radius': 0.12,
        'trigger_distance': 0.18
    },
    'hihat': {
        'center': np.array([0.3, 0.4, 0.0]),
        'radius': 0.10,
        'trigger_distance': 0.15
    },
    'crash': {
        'center': np.array([0.7, 0.4, 0.0]),
        'radius': 0.10,
        'trigger_distance': 0.15
    },
    'tom1': {
        'center': np.array([0.4, 0.5, 0.0]),
        'radius': 0.08,
        'trigger_distance': 0.12
    },
    'tom2': {
        'center': np.array([0.6, 0.5, 0.0]),
        'radius': 0.08,
        'trigger_distance': 0.12
    }
}

# Configurazione Audio
SAMPLE_RATE = 44100
BUFFER_SIZE = 512
AUDIO_CHANNELS = 2

# Configurazione Visualizzazione 3D
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FOV = 60  # Field of view in gradi
NEAR_PLANE = 0.1
FAR_PLANE = 100.0

# Colori (RGB)
COLORS = {
    'background': (20, 20, 30),
    'drum_zone': (100, 150, 200),
    'drum_zone_active': (255, 200, 100),
    'user': (50, 200, 100),
    'grid': (60, 60, 70)
}

# Sensibilità
VELOCITY_THRESHOLD = 0.3  # Velocità minima per triggerare un colpo
COOLDOWN_TIME = 0.1  # Secondi tra un colpo e l'altro (per evitare doppi trigger)

