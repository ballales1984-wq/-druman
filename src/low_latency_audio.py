"""
Low-Latency Audio Engine

Sostituisce pygame.mixer con un sistema audio a bassa latenza:
- python-rtmixer per callback C (evita GIL)
- sounddevice/PortAudio come fallback
- Precomputed audio buffers
- Lock-free queue per eventi
"""

import os
import time
import numpy as np
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass
from collections import deque
from queue import Queue

# Check availability
RTMIXER_AVAILABLE = False
SOUNDDEVICE_AVAILABLE = False

try:
    import rtmixer

    RTMIXER_AVAILABLE = True
except ImportError:
    try:
        import sounddevice as sd

        SOUNDDEVICE_AVAILABLE = True
    except ImportError:
        print(
            "[WARN] Audio engine non disponibile. Installare: pip install python-rtmixer"
        )


@dataclass
class AudioConfig:
    """Configurazione audio"""

    sample_rate: int = 44100
    buffer_size: int = 256  # Piccolo per bassa latenza
    channels: int = 2
    dtype: str = "float32"
    device: Optional[str] = None  # None = default


@dataclass
class DrumSound:
    """Suono di batteria precalcolato"""

    name: str
    buffer: np.ndarray
    velocity_layers: Dict[int, np.ndarray] = None  # {velocity: buffer}


class LowLatencyAudioEngine:
    """
    Motore audio a bassa latenza.

    Usa callback per evitare GIL e garantire continuità.
    """

    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.running = False
        self.sounds: Dict[str, DrumSound] = {}
        self.event_queue: Queue = Queue(maxsize=128)

        self._output_device = None
        self._stream = None

        self._latency_measurements: deque = deque(maxlen=100)
        self._last_timestamp = 0

    def initialize(self) -> bool:
        """
        Inizializza il motore audio.

        Returns:
            True se inizializzato
        """
        if RTMIXER_AVAILABLE:
            return self._init_rtmixer()
        elif SOUNDDEVICE_AVAILABLE:
            return self._init_sounddevice()
        else:
            print("[WARN] Uso pygame.mixer come fallback")
            return self._init_pygame()

    def _init_rtmixer(self) -> bool:
        """Inizializza con rtmixer"""
        try:
            print(
                f"[INFO] Inizializzazione rtmixer (buffer: {self.config.buffer_size})..."
            )

            self._output_device = rtmixer.Open(
                device=self.config.device,
                channels=self.config.channels,
                latency=self.config.buffer_size / self.config.sample_rate,
                sample_rate=self.config.sample_rate,
            )

            self._output_device.set_callback(self._audio_callback)
            self._output_device.start()

            self.running = True
            print("[OK] rtmixer attivo")
            return True

        except Exception as e:
            print(f"[ERR] rtmixer: {e}")
            return self._init_sounddevice()

    def _init_sounddevice(self) -> bool:
        """Inizializza con sounddevice"""
        try:
            print(
                f"[INFO] Inizializzazione sounddevice (buffer: {self.config.buffer_size})..."
            )

            def callback(outdata, frames, time_info, status):
                self._audio_callback(outdata, frames, time_info)

            self._stream = sd.OutputStream(
                device=self.config.device,
                channels=self.config.channels,
                samplerate=self.config.sample_rate,
                blocksize=self.config.buffer_size,
                callback=callback,
                dtype=self.config.dtype,
            )

            self._stream.start()
            self.running = True
            print("[OK] sounddevice attivo")
            return True

        except Exception as e:
            print(f"[ERR] sounddevice: {e}")
            return self._init_pygame()

    def _init_pygame(self) -> bool:
        """Fallback con pygame"""
        try:
            import pygame

            pygame.mixer.init(
                frequency=self.config.sample_rate,
                size=-16,
                channels=self.config.channels,
                buffer=self.config.buffer_size,
            )
            pygame.mixer.set_num_channels(16)

            self.running = True
            print("[OK] pygame.mixer attivo (fallback)")
            return True

        except Exception as e:
            print(f"[ERR] pygame: {e}")
            return False

    def _audio_callback(self, outdata, frames, time_info=None):
        """
        Callback audio (chiamato dal thread nativo).

        Questo è il cuore critico - deve essere velocissimo.
        """
        output = np.zeros((frames, self.config.channels), dtype=np.float32)

        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()

                drum_name = event.get("drum")
                velocity = event.get("velocity", 1.0)
                timestamp = event.get("timestamp", 0)

                if drum_name in self.sounds:
                    sound = self.sounds[drum_name]
                    buffer = sound.get_buffer(velocity)

                    if buffer is not None:
                        pos = 0
                        end = min(pos + len(buffer), frames)
                        output[pos:end] += buffer[: end - pos] * velocity

                # Misura latenza
                if timestamp > 0:
                    latency = time.perf_counter() - timestamp
                    self._latency_measurements.append(latency)

            except:
                break

        # Clip per evitare clipping
        output = np.clip(output, -1.0, 1.0) * 0.9
        outdata[:] = output.astype(np.float32)

    def load_sound(self, name: str, data: np.ndarray, velocities: List[int] = None):
        """
        Carica suono con layer di velocity.

        Args:
            name: Nome suono
            data: Audio buffer
            velocities: Lista velocity per layer (es. [60, 80, 100, 120])
        """
        sound = DrumSound(name=name, buffer=data)

        if velocities:
            sound.velocity_layers = {}
            for vel in velocities:
                gain = vel / 127.0
                sound.velocity_layers[vel] = data * gain

        self.sounds[name] = sound
        print(f"[OK] Suono caricato: {name}")

    def load_wav(self, name: str, path: str, velocities: List[int] = None):
        """Carica suono da file WAV"""
        try:
            import soundfile as sf

            data, sr = sf.read(path)

            if len(data.shape) > 1:
                data = np.mean(data, axis=1)

            if sr != self.config.sample_rate:
                import librosa

                data = librosa.resample(
                    data, orig_sr=sr, target_sr=self.config.sample_rate
                )

            self.load_sound(name, data, velocities)

        except Exception as e:
            print(f"[ERR] Caricamento {path}: {e}")

    def play(self, drum_name: str, velocity: float = 1.0):
        """
        Riproduce suono (thread-safe).

        Args:
            drum_name: Nome suono
            velocity: Velocità (0-1)
        """
        if not self.running:
            return

        event = {
            "drum": drum_name,
            "velocity": velocity,
            "timestamp": time.perf_counter(),
        }

        try:
            self.event_queue.put_nowait(event)
        except:
            pass  # Queue piena - skip

    def stop(self):
        """Ferma il motore"""
        self.running = False

        if self._output_device:
            try:
                self._output_device.stop()
                self._output_device.close()
            except:
                pass

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except:
                pass

        print("[OK] Audio fermato")

    def get_latency_stats(self) -> Dict:
        """Statistiche latenza"""
        if not self._latency_measurements:
            return {"avg": 0, "min": 0, "max": 0, "jitter": 0}

        measurements = list(self._latency_measurements)

        return {
            "avg": np.mean(measurements) * 1000,
            "min": np.min(measurements) * 1000,
            "max": np.max(measurements) * 1000,
            "jitter": np.std(measurements) * 1000,
        }


class PrecomputedDrumPool:
    """
    Pool di suoni precalcolati per evitare sintesi realtime.
    """

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.sounds: Dict[str, np.ndarray] = {}

    def generate_kick(self, pitch: float = 60, duration: float = 0.3) -> np.ndarray:
        """Genera kick precalcolato"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        freq = np.linspace(pitch, pitch * 0.5, len(t))
        wave = np.sin(2 * np.pi * freq * t)
        wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t)

        envelope = np.exp(-t * 10)
        wave *= envelope
        wave = np.clip(wave, -1, 1) * 0.9

        return np.column_stack([wave, wave])

    def generate_snare(self, duration: float = 0.2) -> np.ndarray:
        """Genera snare precalcolato"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 15)
        noise = np.random.normal(0, 0.3, len(t)) * np.exp(-t * 20)

        wave = 0.6 * tone + 0.4 * noise
        wave = np.clip(wave, -1, 1) * 0.85

        return np.column_stack([wave, wave])

    def generate_hihat(self, duration: float = 0.1) -> np.ndarray:
        """Genera hihat precalcolato"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        noise = np.random.normal(0, 0.2, len(t))
        tone = 0.1 * np.sin(2 * np.pi * 8000 * t) * np.exp(-t * 50)

        wave = (noise + tone) * np.exp(-t * 40)
        wave = np.clip(wave, -1, 1) * 0.6

        return np.column_stack([wave, wave])

    def generate_all(self):
        """Genera tutti i suoni base"""
        self.sounds["kick"] = self.generate_kick()
        self.sounds["snare"] = self.generate_snare()
        self.sounds["hihat"] = self.generate_hihat()

        print("[OK] Suoni precalcolati")


def create_low_latency_engine(
    sample_rate: int = 44100, buffer_size: int = 256
) -> LowLatencyAudioEngine:
    """
    Factory per creare engine audio.

    Args:
        sample_rate: Sample rate
        buffer_size: Buffer size (minore = minore latenza)

    Returns:
        LowLatencyAudioEngine
    """
    config = AudioConfig(sample_rate=sample_rate, buffer_size=buffer_size)

    engine = LowLatencyAudioEngine(config)

    if not engine.initialize():
        print("[ERR] Inizializzazione fallita")
        return None

    # Carica suoni precalcolati
    pool = PrecomputedDrumPool(sample_rate)
    pool.generate_all()

    for name, buffer in pool.sounds.items():
        engine.load_sound(name, buffer)

    return engine


if __name__ == "__main__":
    print("=" * 60)
    print("LOW-LATENCY AUDIO ENGINE TEST")
    print("=" * 60)

    engine = create_low_latency_engine(sample_rate=44100, buffer_size=256)

    if engine:
        print("\n[OK] Engine attivo")
        print(f"  Buffer: {engine.config.buffer_size}")
        print(f"  Sample rate: {engine.config.sample_rate}")
        print(
            f"  Latenza stimata: {engine.config.buffer_size / engine.config.sample_rate * 1000:.1f}ms"
        )

        # Test playback
        print("\n[Test] Riproduzione suoni...")
        time.sleep(0.5)
        engine.play("kick", 1.0)

        time.sleep(0.3)
        engine.play("snare", 0.8)

        time.sleep(0.2)
        engine.play("hihat", 0.6)

        time.sleep(1)

        stats = engine.get_latency_stats()
        print(f"\n[Stats] Latenza:")
        print(f"  Avg: {stats['avg']:.2f}ms")
        print(f"  Min: {stats['min']:.2f}ms")
        print(f"  Max: {stats['max']:.2f}ms")
        print(f"  Jitter: {stats['jitter']:.2f}ms")

        engine.stop()
    else:
        print("[ERR] Engine non disponibile")
