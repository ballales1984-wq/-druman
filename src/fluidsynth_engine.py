"""
FluidSynth Audio Engine

Motore audio usando FluidSynth per suoni realistici:
- Carica SoundFont (.sf2)
- Sintesi MIDI via pyFluidSynth
- Output via sounddevice
- Supporta MIDI out per DAW esterni
"""

import os
import time
import numpy as np
from typing import Optional, Dict, List
from dataclasses import dataclass
from queue import Queue
from multiprocessing import Process, Queue as MPQueue

# Check availability
FLUIDSYNTH_AVAILABLE = False
try:
    import fluidsynth

    FLUIDSYNTH_AVAILABLE = True
except (ImportError, FileNotFoundError):
    try:
        import pyfluidsynth

        FLUIDSYNTH_AVAILABLE = True
    except ImportError:
        print("[WARN] pyFluidSynth non disponibile")


SOUNDDEVICE_AVAILABLE = False
try:
    import sounddevice as sd

    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    pass

RTMIDI_AVAILABLE = False
try:
    import rtmidi2

    RTMIDI_AVAILABLE = True
except ImportError:
    try:
        import mido

        RTMIDI_AVAILABLE = True
    except ImportError:
        pass


@dataclass
class FluidSynthConfig:
    """Configurazione FluidSynth"""

    sample_rate: int = 44100
    buffer_size: int = 256
    channels: int = 2
    soundfont_path: Optional[str] = None
    midi_device: Optional[str] = None


class FluidSynthEngine:
    """
    Motore audio FluidSynth.

    Usa SoundFont per suoni realistici.
    """

    DEFAULT_SOUNDFONTS = [
        # Free drum kits from internet
        "https://musicalartifacts.com/artefacts/3/Training-1.sf2",
        "https://musicalartifacts.com/artefacts/6/Training-2.sf2",
    ]

    def __init__(self, config: Optional[FluidSynthConfig] = None):
        self.config = config or FluidSynthConfig()
        self.synth = None
        self.running = False

        self.event_queue: Queue = Queue(maxsize=128)

        self._stream = None

        # MIDI notes per componenti
        self.drum_notes = {
            "kick": 36,
            "snare": 38,
            "hihat": 42,
            "crash": 49,
            "tom1": 48,
            "tom2": 45,
        }

    def initialize(self) -> bool:
        """Inizializza il motore"""
        if not FLUIDSYNTH_AVAILABLE:
            print("[WARN] pyFluidSynth non installato")
            return self._init_fallback()

        try:
            print("[INFO] Inizializzazione FluidSynth...")

            import fluidsynth

            self.synth = fluidsynth.Synth()
            self.synth.start(sample_rate=self.config.sample_rate, threads=2)

            # Carica SoundFont
            if self.config.soundfont_path and os.path.exists(
                self.config.soundfont_path
            ):
                self.synth.sfload(self.config.soundfont_path)
                print(f"[OK] SoundFont: {self.config.soundfont_path}")
            else:
                print("[WARN] Nessun SoundFont, uso sintesi base")

            # MIDI out
            if RTMIDI_AVAILABLE and self.config.midi_device:
                self._init_midi_out()

            self.running = True
            print("[OK] FluidSynth attivo")
            return True

        except Exception as e:
            print(f"[ERR] FluidSynth: {e}")
            return self._init_fallback()

    def download_soundfont(
        self, url: str = None, target_dir: str = "sounds"
    ) -> Optional[str]:
        """
        Scarica SoundFont automaticamente.

        Args:
            url: URL del SoundFont (se None, usa default)
            target_dir: Directory dove salvare

        Returns:
            Percorso del file scaricato o None
        """
        import urllib.request

        url = url or self.DEFAULT_SOUNDFONTS[0]

        os.makedirs(target_dir, exist_ok=True)
        filename = url.split("/")[-1]
        target_path = os.path.join(target_dir, filename)

        if os.path.exists(target_path):
            print(f"[INFO] SoundFont già presente: {target_path}")
            return target_path

        print(f"[INFO] Scaricamento SoundFont...")
        print(f"       {url}")

        try:
            urllib.request.urlretrieve(url, target_path)
            print(f"[OK] SoundFont scaricato: {target_path}")
            return target_path
        except Exception as e:
            print(f"[ERR] Download SoundFont: {e}")
            return None

    def _init_fallback(self) -> bool:
        """Fallback con sounddevice"""
        if SOUNDDEVICE_AVAILABLE:
            print("[INFO] Uso sounddevice fallback")
            self.running = True
            return True
        return False

    def _init_midi_out(self):
        """Inizializza MIDI out"""
        try:
            if "rtmidi2" in globals():
                self.midi_out = rtmidi2.MidiOut()
                self.midi_out.open_port(0)
                print("[OK] MIDI out attivo")
        except Exception as e:
            print(f"[WARN] MIDI out: {e}")

    def play(self, drum_name: str, velocity: float = 1.0):
        """
        Riproduce suono.

        Args:
            drum_name: Nome componente
            velocity: Velocità (0-1)
        """
        if not self.running:
            return

        note = self.drum_notes.get(drum_name, 36)
        vel = int(velocity * 127)

        event = {"note": note, "velocity": vel, "timestamp": time.perf_counter()}

        try:
            self.event_queue.put_nowait(event)
        except:
            pass

    def process_events(self):
        """Processa eventi dalla coda"""
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()

                if self.synth and FLUIDSYNTH_AVAILABLE:
                    self.synth.noteon(0, event["note"], 0, event["velocity"])
                    # Note off dopo breve tempo
                    time.sleep(0.1)
                    self.synth.noteoff(0, event["note"], 0)

                # MIDI out
                if hasattr(self, "midi_out") and self.midi_out:
                    self.midi_out.send_noteon(0, event["note"], event["velocity"])
                    time.sleep(0.1)
                    self.midi_out.send_noteoff(0, event["note"])

            except:
                break

    def stop(self):
        """Ferma il motore"""
        self.running = False

        if self.synth:
            self.synth.stop()

        if hasattr(self, "midi_out") and self.midi_out:
            self.midi_out.close_port()

        print("[OK] FluidSynth fermato")


class FluidSynthAudioProcess:
    """
    Processo audio separato per FluidSynth.

    Esegue in processo separato per evitare GIL.
    """

    def __init__(self, config: FluidSynthConfig):
        self.config = config
        self.process: Optional[Process] = None
        self.event_queue: Optional[MPQueue] = None

    def start(self):
        """Avvia processo audio"""
        self.event_queue = MPQueue()

        self.process = Process(
            target=self._audio_loop, args=(self.config, self.event_queue)
        )
        self.process.start()

        print(f"[OK] Processo audio avviato (PID: {self.process.pid})")

    @staticmethod
    def _audio_loop(config: FluidSynthConfig, event_queue: MPQueue):
        """Loop del processo audio"""
        engine = FluidSynthEngine(config)
        engine.initialize()

        while True:
            # Processa eventi
            engine.process_events()
            time.sleep(0.001)

    def stop(self):
        """Ferma processo"""
        if self.process:
            self.process.terminate()
            self.process.join()
            print("[OK] Processo audio fermato")


def create_fluidsynth_engine(
    soundfont: Optional[str] = None, sample_rate: int = 44100
) -> FluidSynthEngine:
    """
    Factory per creare engine FluidSynth.

    Args:
        soundfont: Percorso SoundFont (.sf2)
        sample_rate: Sample rate

    Returns:
        FluidSynthEngine
    """
    config = FluidSynthConfig(sample_rate=sample_rate, soundfont_path=soundfont)

    engine = FluidSynthEngine(config)
    engine.initialize()

    return engine


if __name__ == "__main__":
    print("=" * 60)
    print("FLUIDSYNTH AUDIO ENGINE TEST")
    print("=" * 60)

    engine = create_fluidsynth_engine()

    if engine:
        print("\n[Test] Riproduzione suoni...")

        for drum in ["kick", "snare", "hihat"]:
            print(f"  - {drum}")
            engine.play(drum, 0.8)
            time.sleep(0.3)

        engine.stop()
    else:
        print("[ERR] Engine non disponibile")
        print("Installare: pip install pyfluidsynth python-rtmidi2")
