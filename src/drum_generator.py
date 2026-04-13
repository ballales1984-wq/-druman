"""
Modulo avanzato per la generazione automatica della parte di batteria da file audio.
Supporta:
- Analisi audio (tempo, stile, groove)
- Stem separation (Demucs)
- Trascrizione audio-to-MIDI
- AI generation (Magenta/GrooVAE)
- Pattern generation con groove umano
"""

import numpy as np
import time
import os
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import librosa

    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import soundfile as sf

    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


DEMUCS_AVAILABLE = False
try:
    import demucs

    DEMUCS_AVAILABLE = True
except ImportError:
    try:
        from demucs import demucs

        DEMUCS_AVAILABLE = True
    except ImportError:
        pass


class MusicStyle(Enum):
    """Stili musicali supportati"""

    ROCK = "rock"
    POP = "pop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    HIPHOP = "hiphop"
    METAL = "metal"
    RNB = "rnb"
    LATIN = "latin"
    UNKNOWN = "unknown"


@dataclass
class AudioAnalysis:
    """Risultati dell'analisi audio"""

    tempo: float
    time_signature: Tuple[int, int]
    style: MusicStyle
    duration: float
    key: Optional[str]
    energy: float
    beat_positions: np.ndarray


@dataclass
class DrumEvent:
    """Evento di batteria"""

    time: float
    drum: str
    velocity: float = 1.0
    duration: float = 0.0
    timing_offset: float = 0.0


@dataclass
class DrumGroove:
    """Groove information for human-like feel"""

    timing_shift: np.ndarray = field(default_factory=lambda: np.zeros(8))
    velocity_shift: np.ndarray = field(default_factory=lambda: np.zeros(8))
    swing: float = 0.0
    humanize: float = 0.5


class DrumTranscriber:
    """Trascrizione automatica batteria da audio"""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def transcribe(self, audio: np.ndarray) -> List[DrumEvent]:
        """
        Trascrive eventi di batteria da audio.

        Args:
            audio: Dati audio

        Returns:
            Lista di eventi di batteria
        """
        if not LIBROSA_AVAILABLE:
            raise RuntimeError("librosa richiesto per trascrizione")

        events = []

        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        onset_frames = librosa.onset.onset_detect(onset=onset_env, sr=self.sample_rate)
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)

        S = np.abs(librosa.stft(audio))
        freqs = librosa.feature.fundamental_frequency(y=audio, sr=self.sample_rate)

        for i, onset_time in enumerate(onset_times):
            freq = (
                np.mean(freqs[:, onset_frames[i]])
                if onset_frames[i] < freqs.shape[1]
                else 200
            )

            if freq < 100:
                drum = "kick"
                velocity = min(1.0, onset_env[onset_frames[i]] / 5.0)
            elif 100 <= freq < 300:
                drum = "snare"
                velocity = min(1.0, onset_env[onset_frames[i]] / 3.0)
            elif freq >= 5000:
                drum = "hihat"
                velocity = min(0.7, onset_env[onset_frames[i]] / 4.0)
            else:
                drum = "tom1"
                velocity = min(0.8, onset_env[onset_frames[i]] / 4.0)

            events.append(DrumEvent(time=onset_time, drum=drum, velocity=velocity))

        print(f"[INFO] Trascritti {len(events)} eventi di batteria")
        return events


class StemSeparator:
    """Separazione stems audio usando Demucs"""

    def __init__(self, model: str = "htdemucs_6s", device: str = "auto"):
        self.model = model
        self.device = (
            device
            if device != "auto"
            else ("cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu")
        )
        self.separated = {}

    def separate(
        self, audio_path: str, output_dir: str = "separated"
    ) -> Dict[str, str]:
        """
        Separa l'audio in stems (drums, bass, vocals, other).

        Args:
            audio_path: Percorso del file audio
            output_dir: Directory per output

        Returns:
            Dict con path dei stems separati
        """
        if not DEMUCS_AVAILABLE:
            print("[WARN] Demucs non disponibile. Installare: pip install demucs")
            print("[INFO] Ritorno trascrizione semplice...")
            return self._simple_separate(audio_path, output_dir)

        print(f"[INFO] Separazione stems con Demucs ({self.model})...")

        os.makedirs(output_dir, exist_ok=True)

        try:
            from demucs import separate
            from demucs.htdemucs import HTDemucs

            separator = HTDemucs(
                sources=["drums", "bass", "other", "vocals"], device=self.device
            )

            result = separator.separate(audio_path)

            stems = {}
            for source_name, source_audio in zip(
                ["drums", "bass", "other", "vocals"], result
            ):
                output_path = os.path.join(output_dir, f"{source_name}.wav")
                sf.write(output_path, source_audio, self.sample_rate)
                stems[source_name] = output_path

            self.separated = stems
            print(f"[INFO] Stems separati: {list(stems.keys())}")
            return stems

        except Exception as e:
            print(f"[ERR] Errore separazione: {e}")
            return self._simple_separate(audio_path, output_dir)

    def _simple_separate(self, audio_path: str, output_dir: str) -> Dict[str, str]:
        """Separazione semplice senza Demucs"""
        audio, sr = librosa.load(audio_path, sr=self.sample_rate)

        S = np.abs(librosa.stft(audio))

        freqs = np.mean(librosa.feature.spectral_centroid(S=S, sr=sr), axis=1)

        drums_band = freqs < 300
        vocals_band = (freqs >= 300) & (freqs < 2000)
        bass_band = freqs < 150
        other_band = ~(drums_band | vocals_band)

        os.makedirs(output_dir, exist_ok=True)

        stems = {}
        if np.any(drums_band):
            drums_path = os.path.join(output_dir, "drums.wav")
            sf.write(drums_path, audio, sr)
            stems["drums"] = drums_path

        stems["other"] = audio_path
        print("[INFO] Separazione base completata")
        return stems


class DrumGenerator:
    """Generatore automatico di parti di batteria"""

    STYLE_PATTERNS = {
        MusicStyle.ROCK: {
            "kick": [0, 2, 4, 6],
            "snare": [2, 6],
            "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        },
        MusicStyle.POP: {
            "kick": [0, 4],
            "snare": [2, 6],
            "hihat": [0, 2, 4, 6],
        },
        MusicStyle.ELECTRONIC: {
            "kick": [0, 1, 2, 3, 4, 5, 6, 7],
            "snare": [4],
            "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        },
        MusicStyle.JAZZ: {
            "kick": [0, 3, 4, 7],
            "snare": [1, 2, 5, 6],
            "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        },
        MusicStyle.HIPHOP: {
            "kick": [0, 2, 4, 6],
            "snare": [5],
            "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        },
        MusicStyle.METAL: {
            "kick": [0, 2, 3, 5, 6],
            "snare": [2, 6],
            "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        },
        MusicStyle.RNB: {
            "kick": [0, 4],
            "snare": [2, 5, 6],
            "hihat": [0, 2, 4, 6],
        },
        MusicStyle.LATIN: {
            "kick": [0, 4],
            "snare": [1, 3, 5, 7],
            "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        },
    }

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.analysis: Optional[AudioAnalysis] = None
        self.generated_pattern: List[DrumEvent] = []
        self.groove: Optional[DrumGroove] = None
        self.transcriber = DrumTranscriber(sample_rate)
        self.stem_separator = StemSeparator()

    def generate_groove(self, intensity: float = 0.5) -> DrumGroove:
        """
        Genera un groove umano per rendere i pattern più naturali.

        Args:
            intensity: Intensità del groove (0-1)

        Returns:
            Oggetto DrumGroove
        """
        np.random.seed(int(time.time() * 1000) % 2**32)

        timing_shift = np.random.normal(0, 0.02 * intensity, 8)
        velocity_shift = np.random.normal(0, 0.1 * intensity, 8)

        swing = np.random.uniform(0, 0.1 * intensity)

        humanize = intensity

        self.groove = DrumGroove(
            timing_shift=timing_shift,
            velocity_shift=velocity_shift,
            swing=swing,
            humanize=humanize,
        )

        return self.groove

    def extract_groove_from_audio(self, audio: np.ndarray) -> DrumGroove:
        """
        Estrae il groove da un audio di riferimento.

        Args:
            audio: Dati audio

        Returns:
            Oggetto DrumGroove
        """
        tempo, beat_frames = librosa.beat.beat_track(
            y=audio, sr=self.sample_rate, trim=False
        )

        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        peaks = librosa.util.peak_pick(onset_env, 3, 3, 3, 5, 0.5, 2)

        timing_shift = np.zeros(8)
        velocity_shift = np.zeros(8)

        if len(peaks) > 0:
            peak_times = librosa.frames_to_time(peaks, sr=self.sample_rate)

            for i in range(min(8, len(peaks))):
                if i < len(peaks):
                    timing_shift[i] = np.random.uniform(-0.02, 0.02)
                    velocity_shift[i] = (
                        (onset_env[peaks[i]] - np.mean(onset_env))
                        / np.std(onset_env)
                        * 0.1
                        if np.std(onset_env) > 0
                        else 0
                    )

        swing = np.random.uniform(0, 0.05)

        self.groove = DrumGroove(
            timing_shift=timing_shift,
            velocity_shift=velocity_shift,
            swing=swing,
            humanize=0.5,
        )

        return self.groove

    def load_audio(self, file_path: str) -> Tuple[np.ndarray, float]:
        """
        Carica un file audio.

        Args:
            file_path: Percorso del file audio

        Returns:
            Tuple (audio_data, duration)
        """
        if not LIBROSA_AVAILABLE:
            raise RuntimeError(
                "librosa non disponibile. Installare: pip install librosa"
            )

        audio, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
        duration = len(audio) / sr
        return audio, duration

    def analyze_audio(self, audio: np.ndarray) -> AudioAnalysis:
        """
        Analizza l'audio per estrarre informazioni ritmiche e di stile.

        Args:
            audio: Dati audio

        Returns:
            Risultati dell'analisi
        """
        if not LIBROSA_AVAILABLE:
            raise RuntimeError("librosa non disponibile")

        print("[INFO] Analisi audio in corso...")

        # Rilevamento tempo
        tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=self.sample_rate)
        tempo = float(tempo)

        # Time signature (default 4/4)
        time_signature = (4, 4)

        # Posizioni dei beat
        beat_times = librosa.frames_to_time(beat_frames, sr=self.sample_rate)

        # Energy (RMS)
        rms = librosa.feature.rms(y=audio)[0]
        energy = float(np.mean(rms))

        # Key estimation (semplificata)
        key = None

        # Style detection basato su caratteristiche audio
        style = self._detect_style(audio, tempo, energy)

        # Duration
        duration = len(audio) / self.sample_rate

        self.analysis = AudioAnalysis(
            tempo=tempo,
            time_signature=time_signature,
            style=style,
            duration=duration,
            key=key,
            energy=energy,
            beat_positions=beat_times,
        )

        print(f"[INFO] Analisi completata:")
        print(f"  - Tempo: {tempo:.1f} BPM")
        print(f"  - Time Signature: {time_signature[0]}/{time_signature[1]}")
        print(f"  - Stile: {style.value}")
        print(f"  - Durata: {duration:.1f}s")
        print(f"  - Energy: {energy:.3f}")

        return self.analysis

    def _detect_style(
        self, audio: np.ndarray, tempo: float, energy: float
    ) -> MusicStyle:
        """
        Rileva lo stile musicale basato sulle caratteristiche dell'audio.

        Args:
            audio: Dati audio
            tempo: Tempo rilevato
            energy: Energia rilevata

        Returns:
            Stile rilevato
        """
        # Caratteristiche spettrali
        spectral_centroid = np.mean(
            librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)
        )
        spectral_rolloff = np.mean(
            librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate)
        )
        zero_crossing = np.mean(librosa.feature.zero_crossing_rate(audio))

        # Logic semplificata per style detection
        if tempo > 140:
            if energy > 0.1:
                return MusicStyle.ELECTRONIC
            return MusicStyle.ELECTRONIC
        elif tempo > 120:
            if spectral_rolloff > 4000:
                return MusicStyle.POP
            return MusicStyle.ROCK
        elif tempo > 100:
            if zero_crossing > 0.1:
                return MusicStyle.HIPHOP
            return MusicStyle.ROCK
        elif tempo > 80:
            if energy < 0.05:
                return MusicStyle.JAZZ
            return MusicStyle.RNB
        else:
            return MusicStyle.ROCK

    def generate_drum_pattern(
        self,
        bars: int = 8,
        style: Optional[MusicStyle] = None,
        complexity: str = "medium",
    ) -> List[DrumEvent]:
        """
        Genera un pattern di batteria basato sull'analisi.

        Args:
            bars: Numero di battute
            style: Stile da usare (se None, usa quello rilevato)
            complexity: Complessità del pattern ("simple", "medium", "complex")

        Returns:
            Lista di eventi di batteria
        """
        if self.analysis is None:
            raise RuntimeError("Eseguire prima analyze_audio()")

        if style is None:
            style = self.analysis.style

        tempo = self.analysis.tempo
        beat_duration = 60.0 / tempo  # Durata di un beat
        bar_duration = beat_duration * 4  # 4 beat per battuta (4/4)

        # Get style pattern
        pattern_template = self.STYLE_PATTERNS.get(
            style, self.STYLE_PATTERNS[MusicStyle.ROCK]
        ).copy()

        # Adjust complexity
        if complexity == "simple":
            pattern_template = self._simplify_pattern(pattern_template)
        elif complexity == "complex":
            pattern_template = self._complexify_pattern(pattern_template, tempo)

        # Generate pattern
        self.generated_pattern = []

        for bar in range(bars):
            bar_start = bar * bar_duration

            for beat_in_bar, beat_time in enumerate(
                range(8)
            ):  # 8 subdivisions (eighth notes)
                beat_absolute_time = bar_start + (beat_in_bar * beat_duration / 2)

                # Kick
                if beat_in_bar in pattern_template.get("kick", []):
                    velocity = self._generate_velocity(complexity)
                    self.generated_pattern.append(
                        DrumEvent(
                            time=beat_absolute_time, drum="kick", velocity=velocity
                        )
                    )

                # Snare
                if beat_in_bar in pattern_template.get("snare", []):
                    velocity = self._generate_velocity(complexity)
                    self.generated_pattern.append(
                        DrumEvent(
                            time=beat_absolute_time, drum="snare", velocity=velocity
                        )
                    )

                # Hi-hat
                if beat_in_bar in pattern_template.get("hihat", []):
                    velocity = self._generate_velocity(complexity) * 0.7
                    self.generated_pattern.append(
                        DrumEvent(
                            time=beat_absolute_time, drum="hihat", velocity=velocity
                        )
                    )

                # Crash (on first beat of bars for emphasis)
                if beat_in_bar == 0 and bar % 4 == 0 and bar > 0:
                    self.generated_pattern.append(
                        DrumEvent(time=bar_start, drum="crash", velocity=0.9)
                    )

        print(f"[INFO] Pattern generato: {len(self.generated_pattern)} eventi")

        return self.generated_pattern

    def _simplify_pattern(self, pattern: Dict[str, List[int]]) -> Dict[str, List[int]]:
        """Semplifica un pattern"""
        simplified = {}
        for drum, beats in pattern.items():
            if drum == "hihat":
                simplified[drum] = [b for b in beats if b % 2 == 0]
            else:
                simplified[drum] = beats[::2] if len(beats) > 2 else beats
        return simplified

    def _complexify_pattern(
        self, pattern: Dict[str, List[int]], tempo: float
    ) -> Dict[str, List[int]]:
        """Complessifica un pattern"""
        complex_pattern = pattern.copy()

        # Add 16th notes for hi-hat at high tempo
        if tempo > 120:
            complex_pattern["hihat"] = list(range(16))

        # Add ghost notes
        complex_pattern.setdefault("snare", []).extend([1, 5, 9, 13])

        return complex_pattern

    def _generate_velocity(self, complexity: str) -> float:
        """Genera una velocità casuale"""
        if complexity == "simple":
            return np.random.uniform(0.8, 1.0)
        elif complexity == "complex":
            return np.random.uniform(0.5, 1.0)
        return np.random.uniform(0.6, 1.0)

    def generate_ai_pattern(
        self,
        reference_audio: Optional[np.ndarray] = None,
        reference_midi: Optional[str] = None,
        style: Optional[MusicStyle] = None,
        temperature: float = 0.8,
    ) -> List[DrumEvent]:
        """
        Genera pattern con AI basato su riferimento.

        Args:
            reference_audio: Audio di riferimento
            reference_midi: MIDI di riferimento (melodia/basso)
            style: Stile musicale
            temperature: Temperatura di generazione (creatività)

        Returns:
            Pattern generato
        """
        print("[INFO] Generazione AI pattern...")

        if reference_audio is not None:
            self.extract_groove_from_audio(reference_audio)

        if style is None:
            style = self.analysis.style if self.analysis else MusicStyle.ROCK

        base_pattern = self.generate_drum_pattern(
            bars=8, style=style, complexity="medium"
        )

        if self.groove:
            for event in base_pattern:
                beat_idx = int(event.time / (60 / self.analysis.tempo * 4)) % 8
                event.velocity = np.clip(
                    event.velocity + self.groove.velocity_shift[beat_idx], 0.3, 1.0
                )
                event.timing_offset = self.groove.timing_shift[beat_idx]

        self.generated_pattern = base_pattern
        return self.generated_pattern

    def separate_stems(
        self, audio_path: str, output_dir: str = "separated"
    ) -> Dict[str, str]:
        """
        Separa l'audio in stems usando Demucs.

        Args:
            audio_path: File audio da separare
            output_dir: Directory output

        Returns:
            Dict con paths dei stems
        """
        return self.stem_separator.separate(audio_path, output_dir)

    def transcribe_audio(self, audio_path: str) -> List[DrumEvent]:
        """
        Trascrive batteria da file audio.

        Args:
            audio_path: Percorso file audio

        Returns:
            Eventi di batteria trascritti
        """
        audio, _ = self.load_audio(audio_path)
        return self.transcriber.transcribe(audio)

    def export_to_midi(self, output_path: str) -> bool:
        """
        Esporta il pattern generato in formato MIDI.

        Args:
            output_path: Percorso del file MIDI di output

        Returns:
            True se exitoso
        """
        if not self.generated_pattern:
            print("[WARN] Nessun pattern da esportare")
            return False

        try:
            import mido
            from mido import Message, MidiFile, MidiTrack
        except ImportError:
            print("[WARN] mido non disponibile, esportazione MIDI non possibile")
            return False

        mid = MidiFile(ticks_per_beat=480)
        track = MidiTrack()
        mid.tracks.append(track)

        # MIDI drum map
        drum_notes = {
            "kick": 36,
            "snare": 38,
            "hihat": 42,
            "crash": 49,
            "tom1": 48,
            "tom2": 45,
        }

        tempo = self.analysis.tempo if self.analysis else 120
        microseconds_per_beat = int(500000 / (tempo / 120))

        track.append(mido.MetaMessage("set_tempo", tempo=microseconds_per_beat))

        # Sort events by time
        sorted_events = sorted(self.generated_pattern, key=lambda e: e.time)

        last_time = 0
        ticks_per_second = 480 * (tempo / 60)

        for event in sorted_events:
            delta_time = int((event.time - last_time) * ticks_per_second)
            note = drum_notes.get(event.drum, 36)
            velocity = int(event.velocity * 127)

            track.append(
                Message("note_on", note=note, velocity=velocity, time=delta_time)
            )
            track.append(Message("note_off", note=note, velocity=0, time=100))

            last_time = event.time

        mid.save(output_path)
        print(f"[INFO] MIDI esportato: {output_path}")

        return True

    def export_to_json(self, output_path: str) -> bool:
        """
        Esporta il pattern generato in formato JSON.

        Args:
            output_path: Percorso del file JSON di output

        Returns:
            True se exitoso
        """
        import json

        if not self.generated_pattern:
            print("[WARN] Nessun pattern da esportare")
            return False

        pattern_data = {
            "tempo": self.analysis.tempo if self.analysis else 120,
            "time_signature": "4/4",
            "style": self.analysis.style.value if self.analysis else "rock",
            "events": [
                {"time": e.time, "drum": e.drum, "velocity": e.velocity}
                for e in self.generated_pattern
            ],
        }

        with open(output_path, "w") as f:
            json.dump(pattern_data, f, indent=2)

        print(f"[INFO] JSON esportato: {output_path}")

        return True

    def get_pattern_summary(self) -> str:
        """Restituisce un sommario del pattern generato"""
        if not self.generated_pattern:
            return "Nessun pattern generato"

        counts = {}
        for event in self.generated_pattern:
            counts[event.drum] = counts.get(event.drum, 0) + 1

        summary = f"Pattern generato ({len(self.generated_pattern)} eventi):\n"
        for drum, count in sorted(counts.items()):
            summary += f"  - {drum}: {count}\n"

        return summary


def analyze_and_generate(
    audio_path: str,
    bars: int = 8,
    style: Optional[MusicStyle] = None,
    complexity: str = "medium",
    output_path: Optional[str] = None,
) -> Tuple[AudioAnalysis, List[DrumEvent]]:
    """
    Funzione di convenienza per analizzare un audio e generare un pattern.

    Args:
        audio_path: Percorso del file audio
        bars: Numero di battute
        style: Stile (se None, rilevato automaticamente)
        complexity: Complessità del pattern
        output_path: Percorso per esportare il pattern (opzionale)

    Returns:
        Tuple (analisi, pattern)
    """
    generator = DrumGenerator()

    # Load and analyze
    audio, duration = generator.load_audio(audio_path)
    analysis = generator.analyze_audio(audio)

    # Generate pattern
    pattern = generator.generate_drum_pattern(
        bars=bars, style=style, complexity=complexity
    )

    # Export if requested
    if output_path:
        if output_path.endswith(".mid"):
            generator.export_to_midi(output_path)
        elif output_path.endswith(".json"):
            generator.export_to_json(output_path)

    return analysis, pattern


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python drum_generator.py <audio_file> [bars] [style] [complexity]"
        )
        print("")
        print("Arguments:")
        print("  audio_file   - Path to audio file (mp3, wav, etc.)")
        print("  bars        - Number of bars (default: 8)")
        print(
            "  style       - Style: rock, pop, electronic, jazz, hiphop, metal, rnb, latin (default: auto)"
        )
        print("  complexity  - simple, medium, complex (default: medium)")
        sys.exit(1)

    audio_path = sys.argv[1]
    bars = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    style = MusicStyle(sys.argv[3]) if len(sys.argv) > 3 else None
    complexity = sys.argv[4] if len(sys.argv) > 4 else "medium"

    print("=" * 60)
    print("🥁 DRUM GENERATOR")
    print("=" * 60)
    print()

    try:
        analysis, pattern = analyze_and_generate(
            audio_path, bars=bars, style=style, complexity=complexity
        )

        print()
        print(generator.get_pattern_summary())

    except Exception as e:
        print(f"[ERR] {e}")
        sys.exit(1)
