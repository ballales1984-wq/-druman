"""
Modulo Humanizer - Aggiunge feel umano ai pattern di batteria.
Include micro-timing, velocity variation, swing, ghost notes, e groove.
"""

import numpy as np
import pretty_midi
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class HumanGroove:
    """Configurazione del groove umano"""

    swing: float = 0.0
    timing_shift: float = 0.0
    velocity_shift: float = 0.0
    humanize: float = 0.5
    push_beat: float = 0.0
    pull_beat: float = 0.0


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


class Humanizer:
    """Aggiunge feel umano ai pattern MIDI"""

    def __init__(self, groove: Optional[HumanGroove] = None):
        self.groove = groove or HumanGroove()
        self.swing_amount = 0.0
        self.timing_randomness = 0.01
        self.velocity_randomness = 0.1

    def set_groove(self, groove: HumanGroove):
        """Imposta la configurazione del groove"""
        self.groove = groove
        self.swing_amount = groove.swing

    def apply_groove(
        self, midi: pretty_midi.PrettyMIDI, intensity: float = 0.5
    ) -> pretty_midi.PrettyMIDI:
        """
        Applica il groove al pattern MIDI.

        Args:
            midi: Pattern MIDI
            intensity: Intensità del groove (0-1)

        Returns:
            Pattern MIDI modificato
        """
        for instrument in midi.instruments:
            if instrument.is_drum:
                for note in instrument.notes:
                    self._humanize_note(note, intensity)

        return midi

    def _humanize_note(self, note: pretty_midi.Note, intensity: float):
        """Humanizza una singola nota"""
        note.start += self._get_timing_shift(note.pitch, intensity)
        note.start += self._get_swing_shift(note.start, intensity)

        note.velocity = int(
            np.clip(
                note.velocity + self._get_velocity_shift(note.velocity, intensity),
                20,
                127,
            )
        )

        if note.pitch == MIDI_NOTES["snare"] and note.velocity < 50:
            note.pitch = MIDI_NOTES["rim"]

    def _get_timing_shift(self, pitch: int, intensity: float) -> float:
        """Calcola lo spostamento temporale"""
        shift = np.random.normal(0, self.timing_randomness * intensity)

        if pitch in [MIDI_NOTES["kick"], MIDI_NOTES["snare"]]:
            shift *= 0.5
        elif pitch in [MIDI_NOTES["hihat_closed"], MIDI_NOTES["hihat_open"]]:
            shift *= 1.5

        return shift

    def _get_swing_shift(self, time: float, intensity: float) -> float:
        """Calcola lo swing"""
        beat_position = (time * 2) % 1

        if self.swing_amount > 0:
            if beat_position > 0.4 and beat_position < 0.6:
                return self.swing_amount * intensity * 0.5
            elif beat_position > 0.8:
                return self.swing_amount * intensity * 0.25

        return 0.0

    def _get_velocity_shift(self, base_velocity: int, intensity: float) -> int:
        """Calcola la variazione di velocity"""
        return int(
            np.random.normal(0, base_velocity * self.velocity_randomness * intensity)
        )

    def add_swing(
        self, midi: pretty_midi.PrettyMIDI, swing_amount: float = 0.1
    ) -> pretty_midi.PrettyMIDI:
        """
        Aggiunge swing al pattern.

        Args:
            midi: Pattern MIDI
            swing_amount: Quantità di swing (0-1)

        Returns:
            Pattern MIDI con swing
        """
        self.swing_amount = swing_amount

        for instrument in midi.instruments:
            if instrument.is_drum:
                for note in instrument.notes:
                    beat_pos = int(note.start * 2) % 2

                    if beat_pos == 1:
                        shift = swing_amount * 0.02
                        note.start += shift
                    elif beat_pos == 0:
                        shift = -swing_amount * 0.01
                        note.start += shift

        return midi

    def add_push_pull(
        self, midi: pretty_midi.PrettyMIDI, push: float = 0.0, pull: float = 0.0
    ) -> pretty_midi.PrettyMIDI:
        """
        Aggiunge push (anticipo) e pull (ritardo) ai beat forti.

        Args:
            midi: Pattern MIDI
            push: Quantità di anticipo (0-1)
            pull: Quantità di ritardo (0-1)

        Returns:
            Pattern MIDI modificato
        """
        for instrument in midi.instruments:
            if instrument.is_drum:
                for note in instrument.notes:
                    beat_in_bar = int(note.start) % 4

                    if beat_in_bar == 0:
                        note.start -= push * 0.02
                    elif beat_in_bar == 2:
                        note.start += pull * 0.015

        return midi

    def vary_velocity(
        self, midi: pretty_midi.PrettyMIDI, variation: float = 0.15
    ) -> pretty_midi.PrettyMIDI:
        """
        Varia la velocity casualmente.

        Args:
            midi: Pattern MIDI
            variation: Variazione massima (0-1)

        Returns:
            Pattern MIDI con velocity variata
        """
        for instrument in midi.instruments:
            if instrument.is_drum:
                for note in instrument.notes:
                    var = int(np.random.uniform(-variation, variation) * note.velocity)
                    note.velocity = int(np.clip(note.velocity + var, 40, 127))

        return midi

    def accent_beats(
        self, midi: pretty_midi.PrettyMIDI, beats: List[int] = [0]
    ) -> pretty_midi.PrettyMIDI:
        """
        Accenta certi beat nella battuta.

        Args:
            midi: Pattern MIDI
            beats: Beat da accentare (0-3)

        Returns:
            Pattern MIDI modificato
        """
        for instrument in midi.instruments:
            if instrument.is_drum:
                for note in instrument.notes:
                    beat_in_bar = int(note.start) % 4

                    if beat_in_bar in beats:
                        note.velocity = int(min(127, note.velocity * 1.2))

        return midi

    def extract_groove_from_audio(self, audio_path: str) -> HumanGroove:
        """
        Estrae il groove da un file audio.

        Args:
            audio_path: Percorso del file audio

        Returns:
            Configurazione HumanGroove
        """
        try:
            import librosa

            audio, sr = librosa.load(audio_path, sr=44100)

            onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
            peaks = librosa.util.peak_pick(onset_env, 3, 3, 3, 5, 0.5, 2)

            peak_times = librosa.frames_to_time(peaks, sr=sr)

            timings = []
            for i in range(1, min(len(peaks), 32)):
                timings.append(peak_times[i] - peak_times[i - 1])

            if timings:
                avg_timing = np.mean(timings)
                std_timing = np.std(timings)

                swing = float(np.clip(std_timing / avg_timing * 2, 0, 0.3))
                timing_shift = float(np.clip(std_timing, 0, 0.05))
            else:
                swing = 0.0
                timing_shift = 0.0

            energy = librosa.feature.rms(y=audio, sr=sr)[0]
            velocity_shift = (
                float(np.std(energy) / np.mean(energy)) if np.mean(energy) > 0 else 0.1
            )

            human_groove = HumanGroove(
                swing=swing,
                timing_shift=timing_shift,
                velocity_shift=np.clip(velocity_shift, 0, 0.3),
                humanize=0.7,
                push_beat=0.1,
                pull_beat=0.1,
            )

            print(f"[OK] Groove estratto:")
            print(f"  - Swing: {swing:.2f}")
            print(f"  - Timing shift: {timing_shift:.3f}s")
            print(f"  - Velocity shift: {velocity_shift:.2f}")

            return human_groove

        except Exception as e:
            print(f"[WARN] Errore estrazione groove: {e}")
            return HumanGroove()

    def create_groove_automation(
        self, midi: pretty_midi.PrettyMIDI, sections: List[dict]
    ) -> pretty_midi.PrettyMIDI:
        """
        Crea automazione del groove basata sulle sezioni.

        Args:
            midi: Pattern MIDI
            sections: Sezioni rilevate dall'analisi

        Returns:
            Pattern MIDI con groove variato
        """
        for section in sections:
            position = section.get("position", 0)
            section_type = section.get("type", "verse")

            intensity = 0.5

            if section_type == "chorus":
                intensity = 0.8
            elif section_type == "bridge":
                intensity = 0.3
            elif section_type == "outro":
                intensity = 0.9

            for instrument in midi.instruments:
                if instrument.is_drum:
                    for note in instrument.notes:
                        if abs(note.start - position) < 2:
                            note.velocity = int(note.velocity * intensity)

            self.vary_velocity(midi, variation=intensity * 0.2)

        return midi


def humanize_midi(
    midi_path: str,
    output_path: Optional[str] = None,
    swing: float = 0.0,
    humanize: float = 0.5,
) -> pretty_midi.PrettyMIDI:
    """
    Funzione di convenienza per humanizzare un MIDI.

    Args:
        midi_path: Percorso del MIDI input
        output_path: Percorso del MIDI output
        swing: Quantità di swing
        humanize: Intensità di humanization

    Returns:
        Oggetto PrettyMIDI humanizzato
    """
    midi = pretty_midi.PrettyMIDI(midi_path)

    humanizer = Humanizer()

    if swing > 0:
        humanizer.add_swing(midi, swing)

    if humanize > 0:
        humanizer.apply_groove(midi, humanize)
        humanizer.vary_velocity(midi, humanize * 0.15)

    if output_path:
        midi.write(output_path)
        print(f"[OK] MIDI humanizzato: {output_path}")

    return midi


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python humanizer.py <midi_file> [output.mid] [swing] [humanize]")
        sys.exit(1)

    midi_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    swing = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1
    humanize = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5

    print("=" * 60)
    print("HUMANIZER")
    print("=" * 60)

    midi = humanize_midi(midi_path, output_path, swing, humanize)

    print(f"\n[OK] Processato: {output_path or midi_path}")
