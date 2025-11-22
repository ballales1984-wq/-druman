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
# Configurazione per batterista SEDUTO:
# - Snare a DESTRA (mano destra) - INVERTITO
# - Hi-Hat a SINISTRA (mano sinistra) - INVERTITO
# - Kick con ginocchio/gamba
DRUM_ZONES = {
    'snare': {
        'center': np.array([0.75, 0.5, 0.0]),  # DESTRA - Snare (Rullante)
        'radius': 0.12,
        'trigger_distance': 0.18,
        'position_type': 'horizontal',  # Usa posizione X (sinistra/destra)
        'x_range': (0.64, 0.86),  # Range X per trigger (destra) - INGRANDITO 5% (da 0.65-0.85)
        'y_range': (0.33, 0.67)   # Range Y (altezza media) - INGRANDITO 5% (da 0.35-0.65)
    },
    'hihat': {
        'center': np.array([0.25, 0.5, 0.0]),  # SINISTRA - Hi-Hat
        'radius': 0.12,
        'trigger_distance': 0.18,
        'position_type': 'horizontal',  # Usa posizione X (sinistra/destra)
        'x_range': (0.14, 0.36),  # Range X per trigger (sinistra) - INGRANDITO 5% (da 0.15-0.35)
        'y_range': (0.33, 0.67)   # Range Y (altezza media) - INGRANDITO 5% (da 0.35-0.65)
    },
    'kick': {
        'center': np.array([0.5, 0.85, 0.0]),  # BASSO CENTRO - Kick (ginocchio/gamba)
        'radius': 0.15,
        'trigger_distance': 0.2,
        'position_type': 'knee',  # Usa ginocchio/gamba
        'x_range': (0.28, 0.72),    # Range X (centro) - INGRANDITO 5% (da 0.3-0.7)
        'y_range': (0.665, 1.0)     # Range Y (basso) - INGRANDITO 5% (da 0.7-1.0)
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
VELOCITY_THRESHOLD = 0.2  # Velocità minima per triggerare un colpo (ridotta per migliorare sensibilità)
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

