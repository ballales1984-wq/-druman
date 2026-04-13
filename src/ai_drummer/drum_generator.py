"""
Modulo DrumGenerator - Genera pattern di batteria evolutivi.
Parte da un ritmo base e evolve aggiungendo complessità, ghost notes, fills, etc.
"""

import numpy as np
import pretty_midi
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

try:
    from .analyzer import AudioAnalysis
except ImportError:
    from analyzer import AudioAnalysis


class Complexity(Enum):
    """Livelli di complessità del pattern"""

    BASE = "base"
    MEDIUM = "medium"
    ADVANCED = "advanced"
    EXPERT = "expert"


class MusicStyle(Enum):
    """Stili musicali"""

    ROCK = "rock"
    POP = "pop"
    HIPHOP = "hiphop"
    ELECTRONIC = "electronic"
    JAZZ = "jazz"
    METAL = "metal"
    RNB = "rnb"
    FUNK = "funk"


MIDI_NOTES = {
    "kick": 36,
    "snare": 38,
    "hihat_closed": 42,
    "hihat_open": 46,
    "crash": 49,
    "ride": 51,
    "tom1": 48,
    "tom2": 45,
    "tom_floor": 43,
    "rim": 37,
    "clap": 39,
}


@dataclass
class DrumPattern:
    """Pattern di batteria generato"""

    notes: List[pretty_midi.Note] = field(default_factory=list)
    complexity: Complexity = Complexity.BASE
    style: MusicStyle = MusicStyle.ROCK
    tempo: float = 120.0


STYLE_PATTERNS = {
    MusicStyle.ROCK: {
        "kick": [0, 2, 4, 6],
        "snare": [2, 6],
        "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        "fill_beats": [7],
    },
    MusicStyle.POP: {
        "kick": [0, 4],
        "snare": [2, 6],
        "hihat": [0, 2, 4, 6],
        "fill_beats": [6, 7],
    },
    MusicStyle.HIPHOP: {
        "kick": [0, 1.5, 3, 4, 5.5, 7],
        "snare": [4],
        "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        "fill_beats": [7],
    },
    MusicStyle.ELECTRONIC: {
        "kick": [0, 1, 2, 3, 4, 5, 6, 7],
        "snare": [4],
        "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        "fill_beats": [3, 7],
    },
    MusicStyle.JAZZ: {
        "kick": [0, 3, 4, 7],
        "snare": [1, 2, 5, 6],
        "hihat": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5],
        "fill_beats": [7],
    },
    MusicStyle.METAL: {
        "kick": [0, 1, 2, 3, 4, 5, 6, 7],
        "snare": [2, 6],
        "hihat": [0, 1, 2, 3, 4, 5, 6, 7],
        "fill_beats": [3, 7],
    },
    MusicStyle.RNB: {
        "kick": [0, 4],
        "snare": [2, 5, 6],
        "hihat": [0, 2, 4, 6],
        "fill_beats": [7],
    },
    MusicStyle.FUNK: {
        "kick": [0, 3, 4, 7],
        "snare": [1, 3, 5, 7],
        "hihat": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5],
        "fill_beats": [7],
    },
}


class DrumGenerator:
    """Generatore di pattern di batteria"""

    def __init__(self, analysis: Optional[AudioAnalysis] = None):
        self.analysis = analysis
        self.tempo = analysis.tempo if analysis else 120.0
        self.pattern: Optional[DrumPattern] = None

    def generate(
        self,
        length_bars: int = 8,
        complexity: str = "base",
        style: str = "rock",
        use_analysis: bool = True,
    ) -> pretty_midi.PrettyMIDI:
        """
        Genera un pattern di batteria.

        Args:
            length_bars: Numero di battute
            complexity: Livello di complessità (base, medium, advanced, expert)
            style: Stile musicale
            use_analysis: Usa l'analisi audio per generare

        Returns:
           Oggetto PrettyMIDI
        """
        comp = Complexity(complexity)
        sty = MusicStyle(style)

        if self.analysis and use_analysis:
            self.tempo = self.analysis.tempo

        midi = pretty_midi.PrettyMIDI(initial_tempo=self.tempo)
        drum_track = pretty_midi.Instrument(program=0, is_drum=True)

        beat_duration = 60.0 / self.tempo
        bar_duration = beat_duration * 4

        style_pattern = STYLE_PATTERNS.get(sty, STYLE_PATTERNS[MusicStyle.ROCK])

        for bar in range(length_bars):
            bar_start = bar * bar_duration

            is_fill_bar = self._is_fill_bar(bar, length_bars, comp)
            is_emphasis = self._is_emphasis_bar(bar, length_bars)

            self._generate_bar(
                drum_track,
                bar_start,
                bar_duration,
                beat_duration,
                style_pattern,
                comp,
                is_fill_bar,
                is_emphasis,
                bar,
            )

        midi.instruments.append(drum_track)

        self.pattern = DrumPattern(
            notes=drum_track.notes, complexity=comp, style=sty, tempo=self.tempo
        )

        return midi

    def _is_fill_bar(self, bar: int, total_bars: int, complexity: Complexity) -> bool:
        """Determina se questa battuta deve avere un fill"""
        if complexity == Complexity.BASE:
            return False

        fill_interval = 8 if complexity == Complexity.MEDIUM else 4
        if complexity == Complexity.EXPERT:
            fill_interval = 2

        return bar % fill_interval == fill_interval - 1 and bar < total_bars - 1

    def _is_emphasis_bar(self, bar: int, total_bars: int) -> bool:
        """Battute di enfatizzazione (primo beat, chorus, etc.)"""
        return bar == 0 or (bar + 1) % 4 == 0

    def _generate_bar(
        self,
        track: pretty_midi.Instrument,
        bar_start: float,
        bar_duration: float,
        beat_duration: float,
        style_pattern: Dict,
        complexity: Complexity,
        is_fill_bar: bool,
        is_emphasis: bool,
        bar_number: int,
    ):
        """Genera una battuta di batteria"""
        subdiv = style_pattern.get("hihat", [0, 1, 2, 3, 4, 5, 6, 7])

        for beat_in_bar in range(8):
            beat_time = bar_start + (beat_in_bar * beat_duration / 2)

            is_choked = beat_in_bar in style_pattern.get("kick", [])

            if is_choked:
                vel = 100 if not is_emphasis else 110
                vel = self._add_velocity_variation(vel, complexity)

                track.notes.append(
                    pretty_midi.Note(
                        velocity=vel,
                        pitch=MIDI_NOTES["kick"],
                        start=beat_time,
                        end=beat_time + 0.1,
                    )
                )

            if beat_in_bar in style_pattern.get("snare", []):
                vel = 90 if not is_emphasis else 100
                vel = self._add_velocity_variation(vel, complexity)

                track.notes.append(
                    pretty_midi.Note(
                        velocity=vel,
                        pitch=MIDI_NOTES["snare"],
                        start=beat_time,
                        end=beat_time + 0.1,
                    )
                )

            if beat_in_bar in style_pattern.get("hihat", []):
                vel = 70 + (10 if beat_in_bar % 2 == 0 else 0)
                vel = self._add_velocity_variation(vel, complexity)

                pitch = MIDI_NOTES["hihat_closed"]
                if beat_in_bar == 0 and bar_number == 0:
                    pitch = MIDI_NOTES["crash"]
                elif beat_in_bar == 4 and is_emphasis:
                    pitch = MIDI_NOTES["ride"]
                elif complexity != Complexity.BASE and beat_in_bar % 2 == 1:
                    pitch = MIDI_NOTES["hihat_open"]

                track.notes.append(
                    pretty_midi.Note(
                        velocity=vel,
                        pitch=pitch,
                        start=beat_time,
                        end=beat_time
                        + (0.05 if pitch == MIDI_NOTES["hihat_closed"] else 0.3),
                    )
                )

            if is_fill_bar and self._is_fill_beat(beat_in_bar, complexity):
                self._add_fill_note(track, beat_time, complexity)

        self._add_ghost_notes(track, bar_start, bar_duration, complexity)

    def _add_velocity_variation(
        self, base_velocity: int, complexity: Complexity
    ) -> int:
        """Aggiunge variazione di velocity basata sulla complessità"""
        if complexity == Complexity.BASE:
            variation = 0
        elif complexity == Complexity.MEDIUM:
            variation = np.random.randint(-10, 10)
        else:
            variation = np.random.randint(-20, 20)

        return int(np.clip(base_velocity + variation, 30, 127))

    def _is_fill_beat(self, beat: int, complexity: Complexity) -> bool:
        """Determina se il beat fa parte del fill"""
        if complexity == Complexity.MEDIUM:
            return beat in [6, 7]
        elif complexity in [Complexity.ADVANCED, Complexity.EXPERT]:
            return beat >= 5
        return False

    def _add_fill_note(
        self, track: pretty_midi.Instrument, beat_time: float, complexity: Complexity
    ):
        """Aggiunge note di fill"""
        toms = [MIDI_NOTES["tom1"], MIDI_NOTES["tom2"], MIDI_NOTES["tom_floor"]]

        velocity = 80 if complexity == Complexity.MEDIUM else 90

        for i, tom in enumerate(toms[:2] if complexity == Complexity.MEDIUM else toms):
            track.notes.append(
                pretty_midi.Note(
                    velocity=velocity - i * 5,
                    pitch=tom,
                    start=beat_time + i * 0.05,
                    end=beat_time + i * 0.05 + 0.15,
                )
            )

    def _add_ghost_notes(
        self,
        track: pretty_midi.Instrument,
        bar_start: float,
        bar_duration: float,
        complexity: Complexity,
    ):
        """Aggiunge ghost notes"""
        if complexity in [Complexity.ADVANCED, Complexity.EXPERT]:
            beat_duration = bar_duration / 4

            for ghostbeat in [1, 3, 5]:
                ghost_time = bar_start + ghostbeat * beat_duration

                track.notes.append(
                    pretty_midi.Note(
                        velocity=np.random.randint(25, 45),
                        pitch=MIDI_NOTES["rim"],
                        start=ghost_time,
                        end=ghost_time + 0.02,
                    )
                )

                if complexity == Complexity.EXPERT and np.random.random() > 0.5:
                    track.notes.append(
                        pretty_midi.Note(
                            velocity=np.random.randint(20, 35),
                            pitch=MIDI_NOTES["snare"],
                            start=ghost_time + beat_duration * 0.5,
                            end=ghost_time + beat_duration * 0.5 + 0.02,
                        )
                    )

    def generate_progressive(
        self, length_bars: int = 8, style: str = "rock"
    ) -> Dict[str, pretty_midi.PrettyMIDI]:
        """
        Genera versioni progressive del pattern.

        Args:
            length_bars: Numero di battute
            style: Stile musicale

        Returns:
            Dict con versioni (base, medium, advanced, expert)
        """
        versions = {}

        for complexity in ["base", "medium", "advanced", "expert"]:
            midi = self.generate(
                length_bars=length_bars, complexity=complexity, style=style
            )
            versions[complexity] = midi

        return versions

    def export(self, output_path: str, complexity: str = "medium") -> bool:
        """
        Esporta il pattern generato.

        Args:
            output_path: Percorso del file MIDI
            complexity: Complessità da esportare

        Returns:
            True se successo
        """
        if self.pattern is None:
            self.generate(complexity=complexity)

        if self.pattern is None:
            return False

        midi = pretty_midi.PrettyMIDI(initial_tempo=self.tempo)
        drum_track = pretty_midi.Instrument(program=0, is_drum=True)

        for note in self.pattern.notes:
            drum_track.notes.append(note)

        midi.instruments.append(drum_track)

        midi.write(output_path)
        print(f"[OK] MIDI esportato: {output_path}")

        return True


def generate_drum_pattern(
    audio_path: Optional[str] = None,
    length_bars: int = 8,
    complexity: str = "medium",
    style: str = "rock",
    output_path: Optional[str] = None,
) -> pretty_midi.PrettyMIDI:
    """
    Funzione di convenienza per generare un pattern di batteria.

    Args:
        audio_path: Percorso del file audio di riferimento
        length_bars: Numero di battute
        complexity: Complessità
        style: Stile
        output_path: Percorso per esportare il MIDI

    Returns:
        Oggetto PrettyMIDI
    """
    analysis = None

    if audio_path:
        from .analyzer import analyze_reference

        analysis = analyze_reference(audio_path)

    generator = DrumGenerator(analysis)
    midi = generator.generate(
        length_bars=length_bars, complexity=complexity, style=style
    )

    if output_path:
        midi.write(output_path)
        print(f"[OK] Pattern esportato: {output_path}")

    return midi


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "Usage: python drum_generator.py [bars] [complexity] [style] [output.mid]"
        )
        print("  bars        - Numero battute (default: 8)")
        print("  complexity - base, medium, advanced, expert")
        print("  style     - rock, pop, hiphop, electronic, jazz, metal, rnb, funk")
        sys.exit(1)

    bars = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    complexity = sys.argv[2] if len(sys.argv) > 2 else "medium"
    style = sys.argv[3] if len(sys.argv) > 3 else "rock"
    output_path = sys.argv[4] if len(sys.argv) > 4 else "output.mid"

    print("=" * 60)
    print("DRUM GENERATOR")
    print("=" * 60)

    midi = generate_drum_pattern(
        length_bars=bars, complexity=complexity, style=style, output_path=output_path
    )

    print(f"\n[OK] Generato: {output_path}")
