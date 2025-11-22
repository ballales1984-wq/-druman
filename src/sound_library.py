"""
Libreria di Suoni di Batteria Modificabile
Permette di caricare, modificare e gestire suoni campionati
"""
import os
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("⚠️  soundfile non installato. Installa con: pip install soundfile")

try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class SoundSample:
    """Classe per rappresentare un campione audio modificabile"""
    
    def __init__(self, name: str, file_path: Optional[str] = None, 
                 audio_data: Optional[np.ndarray] = None, sample_rate: int = 44100):
        """
        Inizializza un campione audio
        
        Args:
            name: Nome del campione
            file_path: Percorso file audio (opzionale)
            audio_data: Dati audio come array numpy (opzionale)
            sample_rate: Frequenza di campionamento
        """
        self.name = name
        self.file_path = file_path
        self.sample_rate = sample_rate
        
        # Dati audio originali
        if audio_data is not None:
            self.original_audio = audio_data.copy()
        elif file_path and os.path.exists(file_path):
            self.original_audio = self._load_audio_file(file_path)
        else:
            self.original_audio = np.array([])
        
        # Dati audio modificati (copia di lavoro)
        self.modified_audio = self.original_audio.copy() if len(self.original_audio) > 0 else np.array([])
        
        # Parametri di modifica
        self.parameters = {
            'volume': 1.0,           # Volume (0-2.0)
            'pitch': 1.0,            # Pitch shift (0.5-2.0)
            'speed': 1.0,            # Velocità riproduzione (0.5-2.0)
            'attack': 0.0,           # Tempo attacco (0-1.0)
            'decay': 1.0,            # Tempo decay (0-1.0)
            'sustain': 1.0,          # Livello sustain (0-1.0)
            'release': 0.0,          # Tempo release (0-1.0)
            'lowpass_freq': 20000,   # Frequenza filtro passa-basso (Hz)
            'highpass_freq': 0,      # Frequenza filtro passa-alto (Hz)
            'reverb': 0.0,           # Livello riverbero (0-1.0)
            'distortion': 0.0,        # Livello distorsione (0-1.0)
            'pan': 0.0,              # Panoramica (-1.0 = sinistra, 1.0 = destra)
        }
        
        # Metadati
        self.metadata = {
            'created': time.time(),
            'modified': time.time(),
            'duration': len(self.original_audio) / self.sample_rate if len(self.original_audio) > 0 else 0.0,
            'channels': 1 if len(self.original_audio.shape) == 1 else self.original_audio.shape[1]
        }
    
    def _load_audio_file(self, file_path: str) -> np.ndarray:
        """Carica file audio"""
        if not SOUNDFILE_AVAILABLE:
            raise ImportError("soundfile non disponibile. Installa con: pip install soundfile")
        
        try:
            data, sr = sf.read(file_path)
            self.sample_rate = sr
            
            # Converti a mono se stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # Normalizza
            if len(data) > 0:
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data = data / max_val
            
            return data
        except Exception as e:
            print(f"❌ Errore caricamento file {file_path}: {e}")
            return np.array([])
    
    def apply_modifications(self) -> np.ndarray:
        """
        Applica tutte le modifiche e restituisce l'audio processato
        
        Returns:
            Array audio modificato
        """
        if len(self.original_audio) == 0:
            return np.array([])
        
        audio = self.original_audio.copy()
        
        # 1. Pitch shift
        if self.parameters['pitch'] != 1.0:
            audio = self._apply_pitch_shift(audio, self.parameters['pitch'])
        
        # 2. Speed change
        if self.parameters['speed'] != 1.0:
            audio = self._apply_speed_change(audio, self.parameters['speed'])
        
        # 3. Envelope (ADSR)
        if any([self.parameters['attack'] > 0, self.parameters['decay'] < 1.0, 
                self.parameters['release'] > 0]):
            audio = self._apply_envelope(audio)
        
        # 4. Filtri
        if self.parameters['lowpass_freq'] < 20000:
            audio = self._apply_lowpass(audio, self.parameters['lowpass_freq'])
        
        if self.parameters['highpass_freq'] > 0:
            audio = self._apply_highpass(audio, self.parameters['highpass_freq'])
        
        # 5. Distorsione
        if self.parameters['distortion'] > 0:
            audio = self._apply_distortion(audio, self.parameters['distortion'])
        
        # 6. Riverbero (semplificato)
        if self.parameters['reverb'] > 0:
            audio = self._apply_reverb(audio, self.parameters['reverb'])
        
        # 7. Volume
        audio = audio * self.parameters['volume']
        
        # 8. Pan (se stereo richiesto)
        if self.parameters['pan'] != 0.0:
            audio = self._apply_pan(audio, self.parameters['pan'])
        
        # Normalizza e limita
        audio = np.clip(audio, -1.0, 1.0)
        
        self.modified_audio = audio
        self.metadata['modified'] = time.time()
        
        return audio
    
    def _apply_pitch_shift(self, audio: np.ndarray, pitch: float) -> np.ndarray:
        """Applica pitch shift"""
        if not SCIPY_AVAILABLE or pitch == 1.0:
            return audio
        
        # Metodo semplice: resample
        indices = np.linspace(0, len(audio), int(len(audio) / pitch))
        return np.interp(indices, np.arange(len(audio)), audio)
    
    def _apply_speed_change(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Cambia velocità riproduzione"""
        if speed == 1.0:
            return audio
        
        indices = np.linspace(0, len(audio) - 1, int(len(audio) / speed))
        return np.interp(indices, np.arange(len(audio)), audio)
    
    def _apply_envelope(self, audio: np.ndarray) -> np.ndarray:
        """Applica envelope ADSR"""
        length = len(audio)
        envelope = np.ones(length)
        
        attack_samples = int(self.parameters['attack'] * length)
        decay_samples = int(self.parameters['decay'] * length)
        release_samples = int(self.parameters['release'] * length)
        sustain_level = self.parameters['sustain']
        
        # Attack
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay
        if decay_samples > attack_samples:
            decay_start = attack_samples
            decay_end = min(decay_samples, length - release_samples)
            if decay_end > decay_start:
                envelope[decay_start:decay_end] = np.linspace(
                    1, sustain_level, decay_end - decay_start
                )
        
        # Sustain (già impostato)
        sustain_start = max(attack_samples, decay_samples)
        sustain_end = length - release_samples
        if sustain_end > sustain_start:
            envelope[sustain_start:sustain_end] = sustain_level
        
        # Release
        if release_samples > 0:
            release_start = max(0, length - release_samples)
            envelope[release_start:] = np.linspace(
                sustain_level, 0, length - release_start
            )
        
        return audio * envelope
    
    def _apply_lowpass(self, audio: np.ndarray, freq: float) -> np.ndarray:
        """Applica filtro passa-basso"""
        if not SCIPY_AVAILABLE or freq >= 20000:
            return audio
        
        nyquist = self.sample_rate / 2
        normalized_freq = freq / nyquist
        b, a = signal.butter(4, normalized_freq, 'low')
        return signal.filtfilt(b, a, audio)
    
    def _apply_highpass(self, audio: np.ndarray, freq: float) -> np.ndarray:
        """Applica filtro passa-alto"""
        if not SCIPY_AVAILABLE or freq <= 0:
            return audio
        
        nyquist = self.sample_rate / 2
        normalized_freq = freq / nyquist
        b, a = signal.butter(4, normalized_freq, 'high')
        return signal.filtfilt(b, a, audio)
    
    def _apply_distortion(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Applica distorsione"""
        if amount == 0:
            return audio
        
        # Soft clipping
        distorted = np.tanh(audio * (1 + amount * 10))
        return audio * (1 - amount) + distorted * amount
    
    def _apply_reverb(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Applica riverbero semplificato"""
        if amount == 0:
            return audio
        
        # Delay semplice con feedback
        delay_samples = int(0.03 * self.sample_rate)  # 30ms delay
        reverb = np.zeros_like(audio)
        
        for i in range(delay_samples, len(audio)):
            reverb[i] = audio[i] + audio[i - delay_samples] * amount * 0.5
        
        return audio * (1 - amount) + reverb * amount
    
    def _apply_pan(self, audio: np.ndarray, pan: float) -> np.ndarray:
        """Applica panoramica (converte a stereo)"""
        if pan == 0.0:
            return audio
        
        # Converti a stereo
        if len(audio.shape) == 1:
            stereo = np.column_stack([audio, audio])
        else:
            stereo = audio.copy()
        
        # Applica pan
        left_gain = np.sqrt((1 - pan) / 2) if pan <= 0 else np.sqrt((1 - pan) / 2) * (1 - abs(pan))
        right_gain = np.sqrt((1 + pan) / 2) if pan >= 0 else np.sqrt((1 + pan) / 2) * (1 - abs(pan))
        
        stereo[:, 0] *= left_gain
        stereo[:, 1] *= right_gain
        
        return stereo
    
    def set_parameter(self, param_name: str, value: float):
        """Imposta un parametro"""
        if param_name in self.parameters:
            self.parameters[param_name] = value
            self.apply_modifications()
    
    def get_parameter(self, param_name: str) -> float:
        """Ottiene un parametro"""
        return self.parameters.get(param_name, 0.0)
    
    def reset_parameters(self):
        """Reset tutti i parametri ai valori di default"""
        self.parameters = {
            'volume': 1.0,
            'pitch': 1.0,
            'speed': 1.0,
            'attack': 0.0,
            'decay': 1.0,
            'sustain': 1.0,
            'release': 0.0,
            'lowpass_freq': 20000,
            'highpass_freq': 0,
            'reverb': 0.0,
            'distortion': 0.0,
            'pan': 0.0,
        }
        self.apply_modifications()
    
    def save(self, file_path: str):
        """Salva il campione modificato"""
        if not SOUNDFILE_AVAILABLE:
            raise ImportError("soundfile non disponibile")
        
        audio = self.apply_modifications()
        if len(audio) > 0:
            sf.write(file_path, audio, self.sample_rate)
    
    def to_dict(self) -> Dict:
        """Converte a dizionario per salvataggio"""
        return {
            'name': self.name,
            'file_path': self.file_path,
            'parameters': self.parameters.copy(),
            'metadata': self.metadata.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SoundSample':
        """Crea da dizionario"""
        sample = cls(
            name=data['name'],
            file_path=data.get('file_path')
        )
        sample.parameters = data.get('parameters', sample.parameters)
        sample.metadata = data.get('metadata', sample.metadata)
        sample.apply_modifications()
        return sample


class SoundLibrary:
    """Libreria di suoni di batteria modificabili"""
    
    def __init__(self, library_path: str = "sounds"):
        """
        Inizializza la libreria
        
        Args:
            library_path: Percorso directory libreria
        """
        self.library_path = Path(library_path)
        self.library_path.mkdir(exist_ok=True)
        
        # Dizionario campioni: {drum_name: SoundSample}
        self.samples: Dict[str, SoundSample] = {}
        
        # Preset salvati
        self.presets: Dict[str, Dict] = {}
        
        # Carica libreria esistente
        self.load_library()
    
    def add_sample(self, drum_name: str, sample: SoundSample):
        """Aggiunge un campione alla libreria"""
        self.samples[drum_name] = sample
        self.save_library()
    
    def load_sample_from_file(self, drum_name: str, file_path: str) -> bool:
        """
        Carica un campione da file
        
        Args:
            drum_name: Nome del componente (kick, snare, etc.)
            file_path: Percorso file audio
        
        Returns:
            True se caricato con successo
        """
        try:
            sample = SoundSample(name=drum_name, file_path=file_path)
            if len(sample.original_audio) > 0:
                self.samples[drum_name] = sample
                self.save_library()
                return True
            return False
        except Exception as e:
            print(f"❌ Errore caricamento campione {drum_name}: {e}")
            return False
    
    def get_sample(self, drum_name: str) -> Optional[SoundSample]:
        """Ottiene un campione"""
        return self.samples.get(drum_name)
    
    def get_audio(self, drum_name: str, apply_mods: bool = True) -> Optional[np.ndarray]:
        """
        Ottiene l'audio di un campione
        
        Args:
            drum_name: Nome del componente
            apply_mods: Se applicare modifiche
        
        Returns:
            Array audio o None
        """
        sample = self.samples.get(drum_name)
        if sample is None:
            return None
        
        if apply_mods:
            return sample.apply_modifications()
        else:
            return sample.original_audio
    
    def remove_sample(self, drum_name: str) -> bool:
        """Rimuove un campione"""
        if drum_name in self.samples:
            del self.samples[drum_name]
            self.save_library()
            return True
        return False
    
    def list_samples(self) -> List[str]:
        """Lista tutti i campioni"""
        return list(self.samples.keys())
    
    def save_library(self):
        """Salva la libreria su disco"""
        library_file = self.library_path / "library.json"
        
        data = {
            'samples': {name: sample.to_dict() for name, sample in self.samples.items()},
            'presets': self.presets
        }
        
        try:
            with open(library_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Errore salvataggio libreria: {e}")
    
    def load_library(self):
        """Carica la libreria da disco"""
        library_file = self.library_path / "library.json"
        
        if not library_file.exists():
            return
        
        try:
            with open(library_file, 'r') as f:
                data = json.load(f)
            
            # Carica campioni
            for name, sample_data in data.get('samples', {}).items():
                try:
                    sample = SoundSample.from_dict(sample_data)
                    self.samples[name] = sample
                except Exception as e:
                    print(f"⚠️  Errore caricamento campione {name}: {e}")
            
            # Carica preset
            self.presets = data.get('presets', {})
            
        except Exception as e:
            print(f"❌ Errore caricamento libreria: {e}")
    
    def save_preset(self, preset_name: str):
        """Salva un preset"""
        preset_data = {}
        for drum_name, sample in self.samples.items():
            preset_data[drum_name] = sample.parameters.copy()
        
        self.presets[preset_name] = preset_data
        self.save_library()
    
    def load_preset(self, preset_name: str) -> bool:
        """Carica un preset"""
        if preset_name not in self.presets:
            return False
        
        preset_data = self.presets[preset_name]
        for drum_name, params in preset_data.items():
            if drum_name in self.samples:
                for param_name, value in params.items():
                    self.samples[drum_name].set_parameter(param_name, value)
        
        return True
    
    def list_presets(self) -> List[str]:
        """Lista tutti i preset"""
        return list(self.presets.keys())
    
    def delete_preset(self, preset_name: str) -> bool:
        """Elimina un preset"""
        if preset_name in self.presets:
            del self.presets[preset_name]
            self.save_library()
            return True
        return False
    
    def export_sample(self, drum_name: str, output_path: str) -> bool:
        """Esporta un campione modificato"""
        sample = self.samples.get(drum_name)
        if sample is None:
            return False
        
        try:
            sample.save(output_path)
            return True
        except Exception as e:
            print(f"❌ Errore esportazione {drum_name}: {e}")
            return False
    
    def import_samples_from_folder(self, folder_path: str, mapping: Optional[Dict[str, str]] = None):
        """
        Importa campioni da una cartella
        
        Args:
            folder_path: Percorso cartella
            mapping: Mappatura {nome_file: drum_name} (opzionale)
        """
        folder = Path(folder_path)
        if not folder.exists():
            print(f"❌ Cartella non trovata: {folder_path}")
            return
        
        # Estensioni supportate
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.aiff']
        
        for file_path in folder.iterdir():
            if file_path.suffix.lower() in audio_extensions:
                # Determina nome componente
                if mapping and file_path.stem in mapping:
                    drum_name = mapping[file_path.stem]
                else:
                    # Prova a dedurre dal nome file
                    name_lower = file_path.stem.lower()
                    drum_name = None
                    for comp in ['kick', 'snare', 'hihat', 'crash', 'tom1', 'tom2']:
                        if comp in name_lower:
                            drum_name = comp
                            break
                    
                    if not drum_name:
                        drum_name = file_path.stem
                
                # Carica campione
                self.load_sample_from_file(drum_name, str(file_path))
                print(f"[OK] Caricato: {drum_name} da {file_path.name}")

