"""
Modulo Analyzer - Analizza la traccia audio di riferimento.
Estrae BPM, beat grid, onsets (accenti), sezioni (stacchi), e feel.
"""

import numpy as np
import librosa
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AudioAnalysis:
    """Risultati dell'analisi audio"""

    tempo: float
    beat_times: np.ndarray
    onsets: np.ndarray
    sections: List[dict]
    duration: float
    energy: np.ndarray
    spectral_centroid: np.ndarray


class AudioAnalyzer:
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.audio: Optional[np.ndarray] = None
        self.analysis: Optional[AudioAnalysis] = None

    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """
        Carica un file audio.

        Args:
            audio_path: Percorso del file audio

        Returns:
            Tuple (audio_data, sample_rate)
        """
        try:
            import soundfile as sf

            audio, sr = sf.read(audio_path)
        except:
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)

        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        self.audio = audio
        self.sample_rate = sr
        return audio, sr

    def analyze(self, audio_path: str) -> AudioAnalysis:
        """
        Analizza la traccia audio.

        Args:
            audio_path: Percorso del file audio

        Returns:
            Risultati dell'analisi
        """
        audio, sr = self.load_audio(audio_path)

        if audio is None:
            raise ValueError(f"Impossibile caricare: {audio_path}")

        self.audio = audio
        self.sample_rate = sr

        print("[INFO] Analisi audio in corso...")

        tempo, beat_frames = librosa.beat.beat_track(
            y=audio, sr=sr, units="time", tightness=100, trim=False
        )

        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        beat_times = beat_times[beat_times < len(audio) / sr]

        onset_env = librosa.onset.onset_strength(y=audio, sr=sr, aggregate=np.median)
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env, sr=sr, units="time"
        )
        onsets = np.array(onset_frames)

        sections = self._detect_sections(audio, sr)

        energy = librosa.feature.rms(y=audio, sr=sr)[0]

        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]

        duration = len(audio) / sr

        self.analysis = AudioAnalysis(
            tempo=float(tempo),
            beat_times=beat_times,
            onsets=onsets,
            sections=sections,
            duration=duration,
            energy=energy,
            spectral_centroid=spectral_centroid,
        )

        self._print_summary()

        return self.analysis

    def _detect_sections(self, audio: np.ndarray, sr: int) -> List[Dict]:
        """
        Rileva cambi di sezione (intro, verse, chorus, bridge, outro).

        Args:
            audio: Dati audio
            sr: Sample rate

        Returns:
            Lista di sezioni rilevate
        """
        energy = librosa.feature.rms(y=audio, sr=sr)[0]

        chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)

        segment_length = len(energy) // 16
        segment_energy = []

        for i in range(16):
            start = i * segment_length
            end = min((i + 1) * segment_length, len(energy))
            segment_energy.append(np.mean(energy[start:end]))

        energy_threshold = np.mean(segment_energy) * 1.2
        section_changes = []

        for i in range(1, len(segment_energy)):
            if abs(segment_energy[i] - segment_energy[i - 1]) > energy_threshold * 0.5:
                time_position = i * segment_length / sr
                section_type = self._classify_section(
                    segment_energy[i], segment_energy[:i] if i > 0 else [0]
                )
                section_changes.append(
                    {
                        "position": time_position,
                        "type": section_type,
                        "energy": float(segment_energy[i]),
                    }
                )

        return section_changes

    def _classify_section(self, energy: float, previous_energies: List[float]) -> str:
        """Classifica il tipo di sezione basato sull'energia"""
        avg_prev = np.mean(previous_energies) if previous_energies else 0

        if energy > avg_prev * 1.5:
            return "chorus"
        elif energy < avg_prev * 0.7:
            return "verse"
        elif energy < avg_prev * 0.5:
            return "bridge"
        elif energy > avg_prev * 2:
            return "outro"
        else:
            return "verse"

    def get_beat_grid(self, subdivisions: int = 4) -> np.ndarray:
        """
        Restituisce una griglia ritmica con suddivisioni.

        Args:
            subdivisions: Numero di suddivisioni per beat

        Returns:
            Array di tempi
        """
        if self.analysis is None:
            raise RuntimeError("Eseguire prima analyze()")

        step = 60.0 / self.analysis.tempo / subdivisions
        duration = self.analysis.duration

        return np.arange(0, duration, step)

    def get_strong_beats(self) -> np.ndarray:
        """
        Restituisce i beat forti (accenti) basati sugli onset.

        Returns:
            Array di beat forti
        """
        if self.analysis is None:
            raise RuntimeError("Eseguire prima analyze()")

        strong_beats = []
        threshold = np.percentile(self.analysis.onsets, 70)

        for onset_time in self.analysis.onsets:
            nearest_beat = self.analysis.beat_times[
                np.argmin(np.abs(self.analysis.beat_times - onset_time))
            ]
            strong_beats.append(nearest_beat)

        return np.unique(np.array(strong_beats))

    def _print_summary(self):
        """Stampa un sommario dell'analisi"""
        if self.analysis is None:
            return

        print(f"[OK] Analisi completata:")
        print(f"  - Tempo: {self.analysis.tempo:.1f} BPM")
        print(f"  - Beat rilevati: {len(self.analysis.beat_times)}")
        print(f"  - Accenti (onsets): {len(self.analysis.onsets)}")
        print(f"  - Sezioni rilevate: {len(self.analysis.sections)}")
        print(f"  - Durata: {self.analysis.duration:.1f}s")

        if self.analysis.sections:
            print(f"\n  Struttura rilevata:")
            for sec in self.analysis.sections[:5]:
                print(f"    - {sec['type']} a {sec['position']:.1f}s")

    def to_dict(self) -> Dict:
        """Esporta l'analisi come dizionario"""
        if self.analysis is None:
            raise RuntimeError("Eseguire prima analyze()")

        return {
            "tempo": self.analysis.tempo,
            "beat_times": self.analysis.beat_times.tolist(),
            "onsets": self.analysis.onsets.tolist(),
            "sections": self.analysis.sections,
            "duration": self.analysis.duration,
        }


def analyze_reference(audio_path: str) -> AudioAnalysis:
    """
    Funzione di convenienza per analizzare un file audio.

    Args:
        audio_path: Percorso del file audio

    Returns:
        Risultati dell'analisi
    """
    analyzer = AudioAnalyzer()
    return analyzer.analyze(audio_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <audio_file>")
        sys.exit(1)

    audio_path = sys.argv[1]

    print("=" * 60)
    print("AUDIO ANALYZER")
    print("=" * 60)

    analyzer = AudioAnalyzer()
    analysis = analyzer.analyze(audio_path)

    print("\n" + analyzer.to_dict())
