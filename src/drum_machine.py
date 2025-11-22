"""
Modulo per la generazione audio della drum machine
"""
import numpy as np
import pygame
import time
from typing import Dict, Optional, List, Tuple
from scipy import signal
from collections import deque

# Import condizionale per SoundLibrary
try:
    from src.sound_library import SoundLibrary
    SOUND_LIBRARY_AVAILABLE = True
except ImportError:
    SOUND_LIBRARY_AVAILABLE = False
    SoundLibrary = None

class DrumMachine:
    """Classe per generare suoni di batteria avanzata"""
    
    def __init__(self, sample_rate: int = 44100, master_volume: float = 0.7, 
                 use_sound_library: bool = False, library_path: str = "sounds"):
        """
        Inizializza la drum machine
        
        Args:
            sample_rate: Frequenza di campionamento audio
            master_volume: Volume master (0-1)
            use_sound_library: Se usare la libreria di suoni invece di sintesi
            library_path: Percorso libreria suoni
        """
        self.sample_rate = sample_rate
        self.channels = 2  # Stereo
        self.master_volume = master_volume
        self.use_sound_library = use_sound_library
        
        # Inizializza Pygame mixer
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=self.channels, buffer=512)
        pygame.mixer.set_num_channels(16)  # Più canali per suoni simultanei
        
        # Dizionario per tracciare i tempi di cooldown
        self.last_hit_times = {}
        self.cooldown_time = 0.05  # Ridotto per risposta più veloce
        
        # Volumi individuali per ogni componente
        self.volumes = {
            'kick': 1.0,
            'snare': 0.9,
            'hihat': 0.7,
            'crash': 0.8,
            'tom1': 0.75,
            'tom2': 0.75
        }
        
        # Libreria suoni (opzionale)
        self.sound_library = None
        if use_sound_library and SOUND_LIBRARY_AVAILABLE:
            try:
                self.sound_library = SoundLibrary(library_path)
                print("[OK] Libreria suoni caricata")
            except Exception as e:
                print(f"[WARN] Errore caricamento libreria: {e}")
                self.use_sound_library = False
        
        # Genera i suoni base (se non usando libreria)
        if not self.use_sound_library:
            self.sounds = self._generate_drum_sounds()
        else:
            self.sounds = {}  # Sarà popolato dalla libreria
        
        # Sistema di registrazione pattern
        self.recording = False
        self.recorded_pattern = []
        self.recording_start_time = 0
        
        # Metronomo
        self.metronome_enabled = False
        self.metronome_bpm = 120
        self.metronome_last_beat = 0
        self.metronome_beat_interval = 60.0 / self.metronome_bpm
    
    def _generate_kick(self, duration: float = 0.4) -> np.ndarray:
        """Genera un suono di kick drum più realistico"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Frequenza base che decresce rapidamente (effetto kick)
        freq_start = 80
        freq_end = 35
        freq = np.linspace(freq_start, freq_end, len(t))
        
        # Genera onda con multiple armoniche per suono più pieno
        wave = np.sin(2 * np.pi * freq * t)
        wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t)  # Seconda armonica
        wave += 0.1 * np.sin(2 * np.pi * freq * 3 * t)  # Terza armonica
        
        # Envelope esponenziale con attacco veloce
        attack_time = 0.01
        attack_samples = int(attack_time * self.sample_rate)
        envelope = np.ones(len(t))
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[attack_samples:] = np.exp(-(t[attack_samples:] - attack_time) * 10)
        wave *= envelope
        
        # Aggiungi rumore per il "punch" e "click"
        noise = np.random.normal(0, 0.15, len(t))
        noise_envelope = np.exp(-t * 25)
        wave += noise * noise_envelope
        
        # Filtro passa-basso per suono più "pieno"
        b, a = signal.butter(2, 200, 'lp', fs=self.sample_rate)
        wave = signal.filtfilt(b, a, wave)
        
        # Normalizza
        wave = np.clip(wave, -1, 1) * 0.9
        
        return wave
    
    def _generate_snare(self, duration: float = 0.25) -> np.ndarray:
        """Genera un suono di snare drum più realistico"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Componente tonale (tamburo) con frequenza che decresce
        freq_start = 250
        freq_end = 180
        freq = np.linspace(freq_start, freq_end, len(t))
        tone = np.sin(2 * np.pi * freq * t)
        tone += 0.4 * np.sin(2 * np.pi * freq * 1.5 * t)  # Armonica
        
        # Envelope con attacco veloce
        attack = 0.005
        attack_samples = int(attack * self.sample_rate)
        tone_envelope = np.ones(len(t))
        tone_envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        tone_envelope[attack_samples:] = np.exp(-(t[attack_samples:] - attack) * 18)
        tone *= tone_envelope
        
        # Componente di rumore (snare wires) con filtro passa-alto
        noise = np.random.normal(0, 0.4, len(t))
        b, a = signal.butter(4, 1000, 'hp', fs=self.sample_rate)
        noise = signal.filtfilt(b, a, noise)
        noise_envelope = np.exp(-t * 30)
        noise *= noise_envelope
        
        # Mix
        wave = 0.6 * tone + 0.4 * noise
        
        # Normalizza
        wave = np.clip(wave, -1, 1) * 0.85
        
        return wave
    
    def _generate_hihat(self, duration: float = 0.12) -> np.ndarray:
        """Genera un suono di hi-hat più realistico"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Rumore bianco con componenti tonali
        noise = np.random.normal(0, 0.25, len(t))
        
        # Aggiungi componenti tonali per suono più definito
        tone1 = 0.1 * np.sin(2 * np.pi * 8000 * t) * np.exp(-t * 50)
        tone2 = 0.05 * np.sin(2 * np.pi * 12000 * t) * np.exp(-t * 60)
        
        # Filtro passa-alto per il suono "bright"
        b, a = signal.butter(6, 6000, 'hp', fs=self.sample_rate)
        noise = signal.filtfilt(b, a, noise)
        
        # Envelope con attacco molto veloce
        attack = 0.001
        attack_samples = int(attack * self.sample_rate)
        envelope = np.ones(len(t))
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[attack_samples:] = np.exp(-(t[attack_samples:] - attack) * 45)
        
        wave = (noise + tone1 + tone2) * envelope
        
        # Normalizza
        wave = np.clip(wave, -1, 1) * 0.7
        
        return wave
    
    def _generate_crash(self, duration: float = 0.8) -> np.ndarray:
        """Genera un suono di crash cymbal più realistico"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Mix di frequenze multiple (armoniche complesse)
        wave = np.zeros(len(t))
        frequencies = [300, 600, 900, 1200, 1800, 2400, 3000]
        weights = [0.3, 0.25, 0.2, 0.15, 0.1, 0.05, 0.05]
        
        for freq, weight in zip(frequencies, weights):
            component = np.sin(2 * np.pi * freq * t)
            # Envelope con decay diverso per ogni frequenza
            envelope = np.exp(-t * (1.5 + freq / 800))
            wave += component * envelope * weight
        
        # Aggiungi rumore bianco filtrato
        noise = np.random.normal(0, 0.2, len(t))
        b, a = signal.butter(4, 2000, 'hp', fs=self.sample_rate)
        noise = signal.filtfilt(b, a, noise)
        noise_envelope = np.exp(-t * 8)
        wave += noise * noise_envelope * 0.3
        
        # Envelope generale
        attack = 0.01
        attack_samples = int(attack * self.sample_rate)
        envelope = np.ones(len(t))
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[attack_samples:] = np.exp(-(t[attack_samples:] - attack) * 2)
        wave *= envelope
        
        # Normalizza
        wave = np.clip(wave, -1, 1) * 0.8
        
        return wave
    
    def _generate_tom(self, pitch: float = 150, duration: float = 0.3) -> np.ndarray:
        """Genera un suono di tom più realistico"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Frequenza fondamentale che decresce
        freq_start = pitch
        freq_end = pitch * 0.65
        freq = np.linspace(freq_start, freq_end, len(t))
        
        # Onda con armoniche
        wave = np.sin(2 * np.pi * freq * t)
        wave += 0.4 * np.sin(2 * np.pi * freq * 1.8 * t)  # Seconda armonica
        wave += 0.2 * np.sin(2 * np.pi * freq * 2.5 * t)  # Terza armonica
        
        # Envelope con attacco
        attack = 0.005
        attack_samples = int(attack * self.sample_rate)
        envelope = np.ones(len(t))
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        envelope[attack_samples:] = np.exp(-(t[attack_samples:] - attack) * 7)
        wave *= envelope
        
        # Aggiungi un po' di rumore per il "thud"
        noise = np.random.normal(0, 0.08, len(t)) * np.exp(-t * 15)
        wave += noise
        
        # Normalizza
        wave = np.clip(wave, -1, 1) * 0.75
        
        return wave
    
    def _generate_drum_sounds(self) -> Dict[str, np.ndarray]:
        """Genera tutti i suoni della batteria"""
        return {
            'kick': self._generate_kick(),
            'snare': self._generate_snare(),
            'hihat': self._generate_hihat(),
            'crash': self._generate_crash(),
            'tom1': self._generate_tom(pitch=180),
            'tom2': self._generate_tom(pitch=160)
        }
    
    def _can_play(self, drum_name: str) -> bool:
        """Verifica se è possibile suonare (cooldown)"""
        current_time = time.time()
        
        if drum_name not in self.last_hit_times:
            return True
        
        time_since_last = current_time - self.last_hit_times[drum_name]
        return time_since_last >= self.cooldown_time
    
    def play_sound(self, drum_name: str, velocity: float = 1.0) -> bool:
        """
        Suona un suono di batteria
        
        Args:
            drum_name: Nome del componente (kick, snare, hihat, etc.)
            velocity: Velocità/intensità del colpo (0-1)
        
        Returns:
            True se il suono è stato riprodotto, False altrimenti
        """
        if not self._can_play(drum_name):
            return False
        
        # Ottieni audio (da libreria o sintesi)
        sound_array = None
        
        if self.use_sound_library and self.sound_library:
            # Usa libreria suoni
            audio = self.sound_library.get_audio(drum_name, apply_mods=True)
            if audio is not None and len(audio) > 0:
                sound_array = audio.copy()
        else:
            # Usa sintesi
            if drum_name not in self.sounds:
                return False
            sound_array = self.sounds[drum_name].copy()
        
        if sound_array is None or len(sound_array) == 0:
            return False
        
        # Applica la velocità al volume con curva non lineare per suono più naturale
        velocity = np.clip(velocity, 0, 1)
        velocity_curve = velocity ** 0.7  # Curva più naturale
        
        # Volume totale = master * componente * velocity
        volume = self.master_volume * self.volumes.get(drum_name, 1.0) * velocity_curve
        
        sound_array = sound_array * volume
        
        # Converti in formato stereo
        if len(sound_array.shape) == 1:
            sound_array = np.column_stack([sound_array, sound_array])
        
        # Converti in formato Pygame
        sound_array = (sound_array * 32767).astype(np.int16)
        
        # Crea e riproduci il suono
        sound = pygame.sndarray.make_sound(sound_array)
        sound.play()
        
        # Registra se in modalità recording
        if self.recording:
            current_time = time.time() - self.recording_start_time
            self.recorded_pattern.append({
                'time': current_time,
                'drum': drum_name,
                'velocity': velocity
            })
        
        # Aggiorna il tempo dell'ultimo colpo
        self.last_hit_times[drum_name] = time.time()
        
        return True
    
    def start_recording(self):
        """Inizia la registrazione di un pattern"""
        self.recording = True
        self.recorded_pattern = []
        self.recording_start_time = time.time()
    
    def stop_recording(self) -> List[Dict]:
        """Ferma la registrazione e restituisce il pattern"""
        self.recording = False
        return self.recorded_pattern.copy()
    
    def play_pattern(self, pattern: List[Dict], loop: bool = False):
        """Riproduce un pattern registrato"""
        if not pattern:
            return
        
        start_time = time.time()
        pattern_duration = pattern[-1]['time'] if pattern else 0
        
        while True:
            current_time = time.time() - start_time
            
            for event in pattern:
                if abs(current_time - event['time']) < 0.01:  # Tolleranza 10ms
                    self.play_sound(event['drum'], event['velocity'])
            
            if current_time > pattern_duration:
                if not loop:
                    break
                start_time = time.time()
    
    def set_metronome(self, enabled: bool, bpm: int = 120):
        """Attiva/disattiva il metronomo"""
        self.metronome_enabled = enabled
        self.metronome_bpm = bpm
        self.metronome_beat_interval = 60.0 / bpm
        self.metronome_last_beat = time.time()
    
    def update_metronome(self):
        """Aggiorna e suona il metronomo se necessario"""
        if not self.metronome_enabled:
            return
        
        current_time = time.time()
        if current_time - self.metronome_last_beat >= self.metronome_beat_interval:
            # Genera un click del metronomo
            t = np.linspace(0, 0.05, int(self.sample_rate * 0.05))
            click = np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 50)
            click = np.clip(click, -1, 1) * 0.3
            
            if len(click.shape) == 1:
                click = np.column_stack([click, click])
            
            click = (click * 32767 * self.master_volume).astype(np.int16)
            sound = pygame.sndarray.make_sound(click)
            sound.play()
            
            self.metronome_last_beat = current_time
    
    def set_volume(self, drum_name: str, volume: float):
        """Imposta il volume di un componente specifico"""
        if drum_name in self.volumes:
            self.volumes[drum_name] = np.clip(volume, 0, 1)
    
    def set_master_volume(self, volume: float):
        """Imposta il volume master"""
        self.master_volume = np.clip(volume, 0, 1)
    
    def stop_all(self):
        """Ferma tutti i suoni"""
        pygame.mixer.stop()

