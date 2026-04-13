"""
Modulo IntentVector - Il cuore del sistema di interpretazione musicale.

Trasforma i dati grezzi dell'audio in un "vettore di intenzione" che rappresenta
cosa il musicista "vuole" suonare in ciascun momento.

Questo è il passaggio chiave da:
    "drum machine" → "AI musician"
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class GrooveType(Enum):
    """Tipi di groove riconoscibili"""

    STRAIGHT = "straight"
    SWING = "swing"
    SHUFFLE = "shuffle"
    BOUNCE = "bounce"
    FUNK = "funk"
    BROKEN = "broken"


class IntensityLevel(Enum):
    """Livelli di intensità"""

    VERY_SOFT = 0.2
    SOFT = 0.4
    MEDIUM = 0.6
    HARD = 0.8
    VERY_HARD = 1.0


class SectionType(Enum):
    """Tipi di sezione musicale"""

    INTRO = "intro"
    VERSE = "verse"
    PRECHORUS = "prechorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    DROP = "drop"
    OUTRO = "outro"
    NONE = "none"


@dataclass
class BeatIntent:
    """Intenzione musicale su un singolo beat"""

    time: float
    strength: float = 0.5
    is_accent: bool = False
    expected_kick: float = 0.0
    expected_snare: float = 0.0
    groove_shift: float = 0.0
    suggestion: str = ""


@dataclass
class IntentVector:
    """
    Vettore di intenzione che rappresenta cosa suonare.

    È l'équivalente del "pensiero di un batterista":
    - dove sono i colpi forti?
    - quanto è energico?
    - che tipo di groove?
    - siamo in un momento di-fill?
    """

    # Timing
    tempo: float = 120.0
    beat_phase: float = 0.0

    # Energia
    overall_energy: float = 0.5
    current_intensity: float = 0.5
    intensity_trend: float = 0.0

    # Groove
    groove_type: GrooveType = GrooveType.STRAIGHT
    swing_amount: float = 0.0

    # Probabilità
    kick_probability: float = 0.5
    snare_probability: float = 0.5
    hihat_probability: float = 0.8

    # Sezione
    section: SectionType = SectionType.NONE
    section_progress: float = 0.0

    # Suggestioni
    suggestions: List[str] = field(default_factory=list)

    # Memoria recente (ultimi beat)
    recent_events: List[BeatIntent] = field(default_factory=list)

    # Stati
    is_fill_moment: bool = False
    is_transition: bool = False
    is_ending: bool = False

    def to_dict(self) -> Dict:
        """Converte in dizionario"""
        return {
            "tempo": self.tempo,
            "beat_phase": self.beat_phase,
            "overall_energy": self.overall_energy,
            "current_intensity": self.current_intensity,
            "intensity_trend": self.intensity_trend,
            "groove_type": self.groove_type.value,
            "swing_amount": self.swing_amount,
            "kick_probability": self.kick_probability,
            "snare_probability": self.snare_probability,
            "hihat_probability": self.hihat_probability,
            "section": self.section.value,
            "section_progress": self.section_progress,
            "suggestions": self.suggestions,
            "is_fill_moment": self.is_fill_moment,
            "is_transition": self.is_transition,
            "is_ending": self.is_ending,
        }


class IntentExtractor:
    """
    Estrae l'intenzione musicale dai dati audio.

    Questo è il "cervello" che interpreta:
    - onde cadono gli accenti
    - quanto è forte il groove
    - quale sezione stiamo suonando
    """

    def __init__(self, window_size: int = 32):
        self.window_size = window_size
        self.history_size = 64

        self.tempo_history = deque(maxlen=self.history_size)
        self.energy_history = deque(maxlen=self.history_size)
        self.onset_history = deque(maxlen=self.history_size)

        self.current_section = SectionType.NONE
        self.section_start_time = 0.0

        self.beat_count = 0
        self.bar_count = 0

    def update(
        self,
        audio_chunk: Optional[np.ndarray] = None,
        beat_times: Optional[np.ndarray] = None,
        onsets: Optional[np.ndarray] = None,
        energy: float = 0.5,
        sr: int = 44100,
    ) -> IntentVector:
        """
        Aggiorna il vettore di intenzione con nuovi dati.

        Args:
            audio_chunk: Chunk audio corrente
            beat_times: Tempi dei beat rilevati
            onsets: Onset rilevati
            energy: Energia corrente (0-1)
            sr: Sample rate

        Returns:
            IntentVector aggiornato
        """
        intent = IntentVector()

        if beat_times is not None and len(beat_times) > 0:
            intent.tempo = self._calculate_tempo(beat_times)
            intent.beat_phase = self._calculate_beat_phase(beat_times)

        self.energy_history.append(energy)
        intent.overall_energy = (
            np.mean(self.energy_history) if self.energy_history else 0.5
        )
        intent.current_intensity = energy
        intent.intensity_trend = self._calculate_trend(self.energy_history)

        if onsets is not None:
            self.onset_history.extend(onsets)
            intent.kick_probability, intent.snare_probability = (
                self._calculate_probabilities(onsets, beat_times)
            )

        intent.groove_type = self._detect_groove_type()
        intent.swing_amount = self._calculate_swing()

        intent.section = self.current_section
        intent.section_progress = self._calculate_section_progress()

        intent.suggestions = self._generate_suggestions(intent)

        intent.is_fill_moment = self._is_fill_moment()
        intent.is_transition = self._is_transition(intent)
        intent.is_ending = self._is_ending()

        return intent

    def _calculate_tempo(self, beat_times: np.ndarray) -> float:
        """Calcola BPM stabile"""
        if len(beat_times) < 2:
            return 120.0

        intervals = np.diff(beat_times)
        intervals = intervals[intervals > 0]

        if len(intervals) == 0:
            return 120.0

        median_interval = np.median(intervals)
        tempo = 60.0 / median_interval

        self.tempo_history.append(tempo)

        return np.median(self.tempo_history) if len(self.tempo_history) > 4 else tempo

    def _calculate_beat_phase(self, beat_times: np.ndarray) -> float:
        """Calcola la fase corrente del beat (0-1)"""
        if len(beat_times) < 2:
            return 0.0

        beat_duration = beat_times[1] - beat_times[0]
        current_time = beat_times[-1]
        phase = (current_time % beat_duration) / beat_duration

        self.beat_count = int(current_time / beat_duration)
        self.bar_count = int(self.beat_count / 4)

        return phase

    def _calculate_trend(self, history: deque) -> float:
        """Calcola trend dell'energia"""
        if len(history) < 4:
            return 0.0

        recent = list(history)[-4:]
        if len(recent) < 2:
            return 0.0

        return recent[-1] - recent[0]

    def _calculate_probabilities(
        self, onsets: np.ndarray, beat_times: Optional[np.ndarray]
    ) -> Tuple[float, float]:
        """Calcola probabilità di kick e snare"""
        if beat_times is None or len(beat_times) < 4:
            return 0.5, 0.5

        kick_prob = 0.3
        snare_prob = 0.3

        beat_positions = []
        for onset in onsets:
            distances = np.abs(beat_times - onset)
            if len(distances) > 0:
                nearest = np.min(distances)
                beat_pos = (onset % (60.0 / self.tempo_history[-1] * 4)) / (
                    60.0 / self.tempo_history[-1]
                )
                beat_positions.append(beat_pos % 1.0)

        if beat_positions:
            for bp in beat_positions:
                if bp < 0.2 or bp > 0.8:
                    kick_prob = 0.8
                elif 0.4 < bp < 0.6:
                    snare_prob = 0.7

        return kick_prob, snare_prob

    def _detect_groove_type(self) -> GrooveType:
        """Rileva il tipo di groove"""
        if len(self.onset_history) < 8:
            return GrooveType.STRAIGHT

        timing_variance = np.std(list(self.onset_history))

        if timing_variance > 0.1:
            return GrooveType.BROKEN
        elif timing_variance > 0.05:
            return GrooveType.FUNK
        elif timing_variance > 0.02:
            return GrooveType.SHUFFLE

        return GrooveType.STRAIGHT

    def _calculate_swing(self) -> float:
        """Calcola quantità di swing"""
        if len(self.onset_history) < 4:
            return 0.0

        variations = []
        for i in range(1, min(len(self.onset_history), 8)):
            variations.append(self.onset_history[i] - self.onset_history[i - 1])

        if len(variations) < 2:
            return 0.0

        odd_even_diff = []
        for i in range(1, len(variations), 2):
            if i < len(variations):
                diff = variations[i] - variations[i - 1] if i > 0 else 0
                odd_even_diff.append(diff)

        return (
            float(np.clip(np.mean(odd_even_diff) * 10, 0, 0.3))
            if odd_even_diff
            else 0.0
        )

    def _calculate_section_progress(self) -> float:
        """Calcola progresso nella sezione corrente"""
        return (self.bar_count % 8) / 8.0

    def _generate_suggestions(self, intent: IntentVector) -> List[str]:
        """Genera suggerimenti basati sull'intenzione"""
        suggestions = []

        if intent.is_fill_moment:
            suggestions.append("fill")

        if intent.intensity_trend > 0.2:
            suggestions.append("build_up")
        elif intent.intensity_trend < -0.2:
            suggestions.append("settle")

        if intent.current_intensity > 0.8:
            suggestions.append("power")

        if intent.section == SectionType.CHORUS and intent.section_progress > 0.8:
            suggestions.append("transition")

        if self.beat_count > 0 and self.beat_count % 16 == 0:
            suggestions.append("new_section")

        return suggestions

    def _is_fill_moment(self) -> bool:
        """Determina se siamo in un momento di fill"""
        if self.beat_count > 0:
            bar_pos = self.beat_count % 4
            if bar_pos == 3:
                return True
        return False

    def _is_transition(self, intent: IntentVector) -> bool:
        """Determina se siamo in una transizione"""
        return intent.section_progress > 0.8 and intent.section != SectionType.NONE

    def _is_ending(self) -> bool:
        """Determina se siamo alla fine"""
        return False

    def detect_section_change(
        self, energy_current: float, energy_previous: float, chroma_change: float = 0.0
    ) -> SectionType:
        """Rileva cambi di sezione"""
        energy_diff = energy_current - energy_previous

        if energy_diff > 0.3:
            new_section = SectionType.CHORUS
        elif energy_diff < -0.3:
            new_section = SectionType.BRIDGE
        elif energy_diff > 0.15:
            new_section = SectionType.DROP
        else:
            return self.current_section

        if new_section != self.current_section:
            self.current_section = new_section

        return self.current_section


class RealtimeIntentProcessor:
    """
    Processore di intenzione in tempo reale.

    Alimenta il sistema con dati in streaming.
    """

    def __init__(self, buffer_size: int = 2048, sample_rate: int = 44100):
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate

        self.intent_extractor = IntentExtractor()

        self.audio_buffer = np.zeros(buffer_size)
        self.buffer_index = 0

        self.current_intent: Optional[IntentVector] = None

    def feed_audio(self, audio_chunk: np.ndarray) -> IntentVector:
        """
        Alimenta con chunk audio e ottieni intenzione corrente.

        Args:
            audio_chunk: Chunk audio

        Returns:
            IntentVector corrente
        """
        chunk_length = len(audio_chunk)

        if chunk_length < self.buffer_size - self.buffer_index:
            self.audio_buffer[self.buffer_index : self.buffer_index + chunk_length] = (
                audio_chunk
            )
            self.buffer_index += chunk_length
        else:
            remaining = self.buffer_size - self.buffer_index
            self.audio_buffer[self.buffer_index :] = audio_chunk[:remaining]

            energy = float(np.mean(np.abs(self.audio_buffer)))

            self.current_intent = self.intent_extractor.update(
                audio_chunk=self.audio_buffer, energy=energy, sr=self.sample_rate
            )

            self.audio_buffer[: chunk_length - remaining] = audio_chunk[remaining:]
            self.buffer_index = chunk_length - remaining

        return self.current_intent

    def feed_beats(
        self, beat_time: float, onsets: List[float], energy: float
    ) -> IntentVector:
        """
        Alimenta con dati di beat (alternativa a audio).

        Args:
            beat_time: Tempo del beat corrente
            onsets: Lista onsets rilevati
            energia: Energia corrente

        Returns:
            IntentVector
        """
        self.current_intent = self.intent_extractor.update(
            beat_times=np.array([beat_time]),
            onsets=np.array(onsets),
            energy=energy,
            sr=self.sample_rate,
        )

        return self.current_intent

    def get_current_intent(self) -> IntentVector:
        """Ottiene l'intenzione corrente"""
        if self.current_intent is None:
            self.current_intent = IntentVector()
        return self.current_intent

    def reset(self):
        """Reset del processore"""
        self.audio_buffer = np.zeros(self.buffer_size)
        self.buffer_index = 0
        self.current_intent = None


def create_intent_from_analysis(analysis_data: Dict) -> IntentVector:
    """
    Crea IntentVector da dati di analisi esistenti.

    Args:
        analysis_data: Dizionario da analyzer

    Returns:
        IntentVector
    """
    intent = IntentVector()

    if "tempo" in analysis_data:
        intent.tempo = analysis_data["tempo"]

    if "onsets" in analysis_data:
        onsets = np.array(analysis_data["onsets"])
        beat_times = analysis_data.get("beat_times", np.array([]))

        intent.kick_probability, intent.snare_probability = (0.6, 0.5)

    if "energy" in analysis_data:
        intent.current_intensity = float(analysis_data["energy"])
        intent.overall_energy = float(analysis_data["energy"])

    if "sections" in analysis_data and analysis_data["sections"]:
        sections = analysis_data["sections"]
        if sections:
            intent.section = SectionType(sections[0].get("type", "verse"))

    return intent


if __name__ == "__main__":
    print("=" * 60)
    print("INTENT VECTOR EXTRACTOR TEST")
    print("=" * 60)

    processor = RealtimeIntentProcessor()

    import time

    for i in range(10):
        test_energy = 0.5 + 0.1 * np.sin(i * 0.5)

        intent = processor.feed_beats(
            beat_time=i * 0.5,
            onsets=[i * 0.5] if i % 2 == 0 else [],
            energy=test_energy,
        )

        print(f"\n[Beat {i}]")
        print(f"  Tempo: {intent.tempo:.1f} BPM")
        print(f"  Kick prob: {intent.kick_probability:.2f}")
        print(f"  Snare prob: {intent.snare_probability:.2f}")
        print(f"  Intensity: {intent.current_intensity:.2f}")
        print(f"  Groove: {intent.groove_type.value}")
        print(f"  Suggestions: {intent.suggestions}")

    print("\n[OK] Test completato")


if __name__ == "__main__":
    main()
