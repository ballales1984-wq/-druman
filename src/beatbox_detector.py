"""
Sistema di rilevamento Beatbox
Rileva suoni vocali (boom, tss, kick, etc.) e li mappa ai suoni della batteria
"""
import numpy as np
import sounddevice as sd
from typing import Dict, List, Optional, Callable
from collections import deque
import time
import threading

class BeatboxDetector:
    """Rileva pattern vocali beatbox e li mappa ai suoni della batteria"""
    
    # Pattern vocali comuni per beatbox
    BEATBOX_PATTERNS = {
        'kick': ['boom', 'bum', 'boot', 'boots', 'b', 'p', 'pff'],
        'snare': ['tss', 'ts', 'ch', 'chh', 't', 'k', 'ka'],
        'hihat': ['t', 'ts', 'tss', 'ch', 'chh', 'tick'],
        'crash': ['tsss', 'chhh', 'sh', 'shh', 'crash'],
        'tom1': ['doom', 'dom', 'dum', 'tom'],
        'tom2': ['tak', 'tack', 'tik', 'tick']
    }
    
    # Frequenze caratteristiche (Hz) per ogni suono
    FREQUENCY_RANGES = {
        'kick': (20, 200),      # Basso
        'snare': (200, 2000),    # Medio-alto
        'hihat': (2000, 8000),   # Alto
        'crash': (1000, 10000),  # Molto alto
        'tom1': (100, 500),      # Basso-medio
        'tom2': (200, 1000)      # Medio
    }
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 chunk_size: int = 1024,
                 threshold: float = 0.3,
                 callback: Optional[Callable] = None):
        """
        Inizializza il detector beatbox
        
        Args:
            sample_rate: Frequenza di campionamento
            chunk_size: Dimensione chunk audio
            threshold: Soglia per rilevamento (0-1)
            callback: Funzione chiamata quando rileva un suono (drum_name, intensity)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.threshold = threshold
        self.callback = callback
        
        # Buffer audio
        self.audio_buffer = deque(maxlen=10)
        
        # Stato
        self.recording = False
        self.stream = None
        self.thread = None
        
        # Statistiche
        self.detections = {name: 0 for name in self.BEATBOX_PATTERNS.keys()}
        
        # Cooldown per evitare doppi trigger
        self.last_trigger_times = {}
        self.cooldown_time = 0.1  # 100ms
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback per audio input"""
        if status:
            print(f"[WARN] Audio status: {status}")
        
        # Converti a numpy array
        audio_data = indata[:, 0]  # Mono
        
        # Aggiungi al buffer
        self.audio_buffer.append(audio_data)
        
        # Analizza
        self._analyze_audio(audio_data)
    
    def _analyze_audio(self, audio_data: np.ndarray):
        """
        Analizza audio per rilevare pattern beatbox
        
        Args:
            audio_data: Dati audio (mono)
        """
        # Calcola energia del segnale
        energy = np.mean(np.abs(audio_data))
        
        if energy < self.threshold:
            return
        
        # FFT per analisi frequenze
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft), 1.0 / self.sample_rate)
        magnitude = np.abs(fft)
        
        # Trova picchi di frequenza
        peak_freqs = self._find_peak_frequencies(freqs, magnitude)
        
        # Rileva pattern
        detected = self._detect_pattern(energy, peak_freqs)
        
        if detected:
            drum_name, intensity = detected
            
            # Cooldown
            current_time = time.time()
            if drum_name in self.last_trigger_times:
                if current_time - self.last_trigger_times[drum_name] < self.cooldown_time:
                    return
            
            self.last_trigger_times[drum_name] = current_time
            self.detections[drum_name] += 1
            
            # Chiama callback
            if self.callback:
                self.callback(drum_name, intensity)
    
    def _find_peak_frequencies(self, freqs: np.ndarray, magnitude: np.ndarray) -> List[float]:
        """Trova frequenze di picco"""
        # Solo frequenze positive
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # Trova picchi (sopra una soglia)
        threshold = np.max(positive_magnitude) * 0.3
        peaks = []
        
        for i in range(1, len(positive_magnitude) - 1):
            if (positive_magnitude[i] > positive_magnitude[i-1] and 
                positive_magnitude[i] > positive_magnitude[i+1] and
                positive_magnitude[i] > threshold):
                peaks.append(positive_freqs[i])
        
        return peaks[:5]  # Top 5 frequenze
    
    def _detect_pattern(self, energy: float, peak_freqs: List[float]) -> Optional[tuple]:
        """
        Rileva pattern beatbox basandosi su energia e frequenze
        
        Args:
            energy: Energia del segnale
            peak_freqs: Frequenze di picco
        
        Returns:
            (drum_name, intensity) se rilevato, None altrimenti
        """
        if not peak_freqs:
            return None
        
        # Frequenza dominante
        dominant_freq = max(peak_freqs) if peak_freqs else 0
        
        # Intensità basata su energia
        intensity = min(1.0, energy * 2.0)
        
        # Mappa frequenza a componente batteria
        best_match = None
        best_score = 0
        
        for drum_name, (freq_min, freq_max) in self.FREQUENCY_RANGES.items():
            if freq_min <= dominant_freq <= freq_max:
                # Score basato su quanto è vicino al centro della range
                center = (freq_min + freq_max) / 2
                distance = abs(dominant_freq - center)
                range_size = freq_max - freq_min
                score = 1.0 - (distance / range_size)
                
                if score > best_score:
                    best_score = score
                    best_match = drum_name
        
        if best_match and best_score > 0.3:
            return (best_match, intensity * best_score)
        
        return None
    
    def start_recording(self):
        """Inizia la registrazione audio"""
        if self.recording:
            return
        
        try:
            self.recording = True
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                dtype=np.float32
            )
            self.stream.start()
            print("[OK] Beatbox detector avviato")
        except Exception as e:
            print(f"[ERROR] Errore avvio beatbox detector: {e}")
            self.recording = False
    
    def stop_recording(self):
        """Ferma la registrazione audio"""
        if not self.recording:
            return
        
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("[OK] Beatbox detector fermato")
    
    def get_statistics(self) -> Dict:
        """Restituisce statistiche rilevamenti"""
        return {
            'total_detections': sum(self.detections.values()),
            'by_component': self.detections.copy(),
            'recording': self.recording
        }
    
    def reset_statistics(self):
        """Reset statistiche"""
        self.detections = {name: 0 for name in self.BEATBOX_PATTERNS.keys()}

