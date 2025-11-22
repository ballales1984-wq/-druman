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
# I pad sono disposti in COLONNA VERTICALE basandosi sull'ALTEZZA (Y)
# X = 0.5 (centro), Y varia da ALTO (0.15) a BASSO (0.95)
# Ogni pad ha un range di altezza per il trigger
DRUM_ZONES = {
    'crash': {
        'center': np.array([0.5, 0.15, 0.0]),  # ALTO - Crash
        'radius': 0.10,
        'trigger_distance': 0.15,
        'height_range': (0.0, 0.25)  # Range altezza Y per trigger (solo Y, ignora X)
    },
    'hihat': {
        'center': np.array([0.5, 0.30, 0.0]),  # ALTO-MEDIO - Hi-Hat
        'radius': 0.10,
        'trigger_distance': 0.15,
        'height_range': (0.20, 0.40)
    },
    'tom2': {
        'center': np.array([0.5, 0.50, 0.0]),  # MEDIO - Tom Alto
        'radius': 0.10,
        'trigger_distance': 0.15,
        'height_range': (0.40, 0.60)
    },
    'snare': {
        'center': np.array([0.5, 0.70, 0.0]),  # MEDIO-BASSO - Snare
        'radius': 0.12,
        'trigger_distance': 0.18,
        'height_range': (0.60, 0.80)
    },
    'tom1': {
        'center': np.array([0.5, 0.85, 0.0]),  # BASSO - Tom Basso
        'radius': 0.10,
        'trigger_distance': 0.15,
        'height_range': (0.75, 0.95)
    },
    'kick': {
        'center': np.array([0.5, 0.95, 0.0]),  # MOLTO BASSO - Kick (piedi)
        'radius': 0.15,
        'trigger_distance': 0.2,
        'height_range': (0.85, 1.0)  # Solo per piedi/caviglie
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

# Configurazione Reaper
REAPER_ENABLED = False  # Abilita connessione a Reaper
REAPER_CONNECTION_TYPE = 'midi'  # 'midi', 'osc', o 'both'
REAPER_MIDI_PORT = None  # None = auto-detect (cerca "Reaper" o usa la prima disponibile)
REAPER_OSC_HOST = '127.0.0.1'
REAPER_OSC_PORT = 8000

# Configurazione Libreria Suoni
USE_SOUND_LIBRARY = True  # Usa libreria suoni invece di sintesi
SOUND_LIBRARY_PATH = "sounds"  # Percorso directory libreria suoni

# Configurazione Visualizzazione
USE_VIDEO_OVERLAY = True  # True = video live con overlay, False = ambiente 3D
BEATBOX_MODE = False  # True = modalità beatbox vocale, False = motion tracking

