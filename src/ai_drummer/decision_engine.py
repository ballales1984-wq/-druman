"""
Modulo DecisionEngine - Il cervello dell'AI drummer.

Riceve l'IntentVector (cosa vuole il musicista) e decide:
- quale drum suonare
- quando
- con quale velocity
- con quale timing

Questo è il cuore del sistema "reattivo":
    INPUT: IntentVector → OUTPUT: drum commands
"""

import numpy as np
import pretty_midi
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

try:
    from .intent_vector import (
        IntentVector,
        IntentExtractor,
        RealtimeIntentProcessor,
        GrooveType,
        IntensityLevel,
        SectionType,
    )
except ImportError:
    from intent_vector import (
        IntentVector,
        IntentExtractor,
        RealtimeIntentProcessor,
        GrooveType,
        IntensityLevel,
        SectionType,
    )


class DrumType(Enum):
    """Tipi di drum"""

    KICK = "kick"
    SNARE = "snare"
    HIHAT_CLOSED = "hihat_closed"
    HIHAT_OPEN = "hihat_open"
    CRASH = "crash"
    RIDE = "ride"
    TOM1 = "tom1"
    TOM2 = "tom2"
    RIM = "rim"
    CLAP = "clap"


@dataclass
class DrumCommand:
    """Comando per suonare un drum"""

    drum: DrumType
    time: float
    velocity: int = 100
    duration: float = 0.1
    timing_offset: float = 0.0
    ghost: bool = False


@dataclass
class DecisionConfig:
    """Configurazione del decision engine"""

    complexity: str = "medium"
    style: str = "rock"
    latency_compensation: float = 0.0
    humanize: float = 0.5
    swing: float = 0.0


class DecisionEngine:
    """
    Motore di decisione che trasforma IntentVector in comandi drum.

    È il "cervello" del sistema:
    - guarda l'intenzione
    - decide cosa suonare
    - applica groove e timing
    """

    MIDI_NOTES = {
        DrumType.KICK: 36,
        DrumType.SNARE: 38,
        DrumType.HIHAT_CLOSED: 42,
        DrumType.HIHAT_OPEN: 46,
        DrumType.CRASH: 49,
        DrumType.RIDE: 51,
        DrumType.TOM1: 48,
        DrumType.TOM2: 45,
        DrumType.RIM: 37,
        DrumType.CLAP: 39,
    }

    STYLE_CONFIGS = {
        "rock": {
            "kick_beats": [0, 2, 4, 6],
            "snare_beats": [2, 6],
            "hihat_pattern": "alternating",
            "fill_chance": 0.3,
        },
        "pop": {
            "kick_beats": [0, 4],
            "snare_beats": [2, 6],
            "hihat_pattern": "offbeat",
            "fill_chance": 0.2,
        },
        "hiphop": {
            "kick_beats": [0, 1.5, 3, 4, 5.5, 7],
            "snare_beats": [4],
            "hihat_pattern": "constant",
            "fill_chance": 0.15,
        },
        "electronic": {
            "kick_beats": [0, 1, 2, 3, 4, 5, 6, 7],
            "snare_beats": [4],
            "hihat_pattern": "constant",
            "fill_chance": 0.4,
        },
        "jazz": {
            "kick_beats": [0, 3, 4, 7],
            "snare_beats": [1, 2, 5, 6],
            "hihat_pattern": "constant",
            "fill_chance": 0.5,
        },
        "funk": {
            "kick_beats": [0, 3, 4, 7],
            "snare_beats": [1, 3, 5, 7],
            "hihat_pattern": "constant",
            "fill_chance": 0.4,
        },
    }

    def __init__(self, config: Optional[DecisionConfig] = None):
        self.config = config or DecisionConfig()
        self.style_config = self.STYLE_CONFIGS.get(
            self.config.style, self.STYLE_CONFIGS["rock"]
        )

        self.history: List[DrumCommand] = []
        self.history_size = 64

        self.command_buffer: List[DrumCommand] = []

        self.beat_counter = 0
        self.bar_counter = 0

    def process_intent(self, intent: IntentVector) -> List[DrumCommand]:
        """
        Processa un IntentVector e genera comandi drum.

        Args:
            intent: Vettore di intenzione

        Returns:
            Lista di comandi da eseguire
        """
        commands = []

        beat_duration = 60.0 / intent.tempo
        bar_duration = beat_duration * 4

        time_in_bar = self.beat_counter % 4
        beat_in_bar = time_in_bar * 2

        if intent.is_fill_moment:
            commands.extend(self._generate_fill(beat_duration))

        if self._should_play_kick(intent, beat_in_bar):
            commands.append(
                self._create_kick_command(beat_duration * beat_in_bar / 2, intent)
            )

        if self._should_play_snare(intent, beat_in_bar):
            commands.append(
                self._create_snare_command(beat_duration * beat_in_bar / 2, intent)
            )

        commands.extend(self._generate_hihats(beat_duration, intent, time_in_bar))

        self._apply_groove(commands, intent)

        self.history.extend(commands)

        self.beat_counter += 1
        if self.beat_counter % 4 == 0:
            self.bar_counter += 1

        return commands

    def _should_play_kick(self, intent: IntentVector, beat_in_bar: int) -> bool:
        """Decide se suonare kick"""
        style_kick = self.style_config["kick_beats"]

        for beat in style_kick:
            if beat_in_bar >= beat and beat_in_bar < beat + 1:
                if np.random.random() < intent.kick_probability:
                    return True

        if intent.is_fill_moment:
            return np.random.random() < 0.3

        return False

    def _should_play_snare(self, intent: IntentVector, beat_in_bar: int) -> bool:
        """Decide se suonare snare"""
        style_snare = self.style_config["snare_beats"]

        for beat in style_snare:
            if beat_in_bar >= beat and beat_in_bar < beat + 1:
                if np.random.random() < intent.snare_probability:
                    return True

        return False

    def _generate_fill(self, beat_duration: float) -> List[DrumCommand]:
        """Genera un fill"""
        commands = []

        fill_patterns = [
            [DrumType.TOM1, DrumType.TOM2, DrumType.SNARE],
            [DrumType.TOM1, DrumType.TOM1, DrumType.SNARE, DrumType.SNARE],
            [DrumType.RIM, DrumType.RIM, DrumType.SNARE],
        ]

        pattern = fill_patterns[int(np.random.random() * len(fill_patterns))]

        base_time = beat_duration * 3

        for i, drum in enumerate(pattern):
            commands.append(
                DrumCommand(
                    drum=drum,
                    time=base_time + i * beat_duration * 0.25,
                    velocity=80 + int(np.random.random() * 20),
                    duration=0.1,
                    ghost=False,
                )
            )

        return commands

    def _generate_hihats(
        self, beat_duration: float, intent: IntentVector, time_in_bar: int
    ) -> List[DrumCommand]:
        """Genera hi-hat pattern"""
        commands = []

        pattern_type = self.style_config["hihat_pattern"]

        if pattern_type == "constant":
            for i in range(8):
                time = time_in_bar * beat_duration * 2 + i * beat_duration * 0.5
                commands.append(
                    DrumCommand(
                        drum=DrumType.HIHAT_CLOSED,
                        time=time,
                        velocity=60 + int(intent.current_intensity * 20),
                        duration=0.05,
                        ghost=False,
                    )
                )

        elif pattern_type == "alternating":
            for i in range(4):
                time = time_in_bar * beat_duration * 2 + i * beat_duration

                commands.append(
                    DrumCommand(
                        drum=DrumType.HIHAT_CLOSED,
                        time=time,
                        velocity=70,
                        duration=0.05,
                        ghost=False,
                    )
                )

                if i < 3:
                    commands.append(
                        DrumCommand(
                            drum=DrumType.HIHAT_CLOSED,
                            time=time + beat_duration * 0.5,
                            velocity=60,
                            duration=0.05,
                            ghost=True,
                        )
                    )

        elif pattern_type == "offbeat":
            for i in range(2):
                time = (
                    time_in_bar * beat_duration * 2 + (i * 2 + 1) * beat_duration * 0.5
                )
                commands.append(
                    DrumCommand(
                        drum=DrumType.HIHAT_CLOSED,
                        time=time,
                        velocity=65,
                        duration=0.05,
                        ghost=False,
                    )
                )

        return commands

    def _create_kick_command(self, time: float, intent: IntentVector) -> DrumCommand:
        """Crea comando kick"""
        base_velocity = 90 + int(intent.current_intensity * 30)

        velocity = base_velocity + int(np.random.uniform(-10, 10))
        velocity = int(np.clip(velocity, 60, 127))

        return DrumCommand(
            drum=DrumType.KICK,
            time=time,
            velocity=velocity,
            duration=0.15,
            timing_offset=0.0,
            ghost=False,
        )

    def _create_snare_command(self, time: float, intent: IntentVector) -> DrumCommand:
        """Crea comando snare"""
        base_velocity = 80 + int(intent.current_intensity * 30)

        velocity = base_velocity + int(np.random.uniform(-10, 10))
        velocity = int(np.clip(velocity, 50, 127))

        ghost = intent.current_intensity < 0.4

        return DrumCommand(
            drum=DrumType.SNARE,
            time=time,
            velocity=velocity,
            duration=0.1,
            timing_offset=0.0,
            ghost=ghost,
        )

    def _apply_groove(self, commands: List[DrumCommand], intent: IntentVector):
        """Apply groove and humanization to commands"""
        if self.config.swing > 0:
            for cmd in commands:
                beat_pos = int(cmd.time * 2) % 2
                if beat_pos == 1:
                    cmd.timing_offset = self.config.swing * 0.02
                elif beat_pos == 0:
                    cmd.timing_offset = -self.config.swing * 0.01

        if self.config.humanize > 0:
            for cmd in commands:
                timing_jitter = np.random.normal(0, 0.01 * self.config.humanize)
                cmd.timing_offset += timing_jitter

                vel_jitter = int(
                    np.random.normal(0, cmd.velocity * 0.1 * self.config.humanize)
                )
                cmd.velocity = int(np.clip(cmd.velocity + vel_jitter, 30, 127))

    def generate_bar(self, intent: IntentVector, bars: int = 1) -> List[DrumCommand]:
        """
        Genera commands per N battute.

        Args:
            intent: IntentVector corrente
            bars: Numero di battute

        Returns:
            Lista di tutti i commands
        """
        all_commands = []

        for _ in range(bars):
            bar_commands = self.process_intent(intent)
            all_commands.extend(bar_commands)

        return all_commands

    def generate_midi(
        self, intent: IntentVector, bars: int = 8
    ) -> pretty_midi.PrettyMIDI:
        """
        Genera MIDI completo.

        Args:
            intent: IntentVector
            bars: Numero battute

        Returns:
            Oggetto PrettyMIDI
        """
        midi = pretty_midi.PrettyMIDI(initial_tempo=intent.tempo)
        drum_track = pretty_midi.Instrument(program=0, is_drum=True)

        for _ in range(bars):
            commands = self.process_intent(intent)

            for cmd in commands:
                note = pretty_midi.Note(
                    velocity=cmd.velocity,
                    pitch=self.MIDI_NOTES[cmd.drum],
                    start=cmd.time + cmd.timing_offset,
                    end=cmd.time + cmd.timing_offset + cmd.duration,
                )
                drum_track.notes.append(note)

        midi.instruments.append(drum_track)
        return midi


class AdaptiveDecisionEngine(DecisionEngine):
    """
    Decision engine adattivo che impara dalle scelte precedenti.

    Mantiene memoria e si adatta al contesto.
    """

    def __init__(self, config: Optional[DecisionConfig] = None):
        super().__init__(config)

        self.recent_decisions: deque = deque(maxlen=32)

        self.pattern_learning = {
            "kick_spacing": [],
            "snare_timing": [],
            "fill_frequency": 0.0,
            "ghost_ratio": 0.0,
        }

    def process_intent(self, intent: IntentVector) -> List[DrumCommand]:
        """Processa intent con apprendimento"""
        commands = super().process_intent(intent)

        self._learn_from_decisions(commands)

        self._adapt_decisions(commands, intent)

        return commands

    def _learn_from_decisions(self, commands: List[DrumCommand]):
        """Impara dai decisioni recenti"""
        if not commands:
            return

        kick_times = [c.time for c in commands if c.drum == DrumType.KICK]
        if len(kick_times) > 1:
            spacing = np.diff(kick_times)
            self.pattern_learning["kick_spacing"].extend(spacing)
            if len(self.pattern_learning["kick_spacing"]) > 16:
                self.pattern_learning["kick_spacing"] = self.pattern_learning[
                    "kick_spacing"
                ][-16:]

        snare_count = sum(1 for c in commands if c.drum == DrumType.SNARE)
        ghost_count = sum(1 for c in commands if c.ghost)

        if snare_count > 0:
            self.pattern_learning["ghost_ratio"] = ghost_count / max(1, snare_count)

        all_commands = list(self.recent_decisions)
        if len(all_commands) > 0:
            fill_count = sum(
                1 for c in all_commands if c.drum in [DrumType.TOM1, DrumType.TOM2]
            )
            self.pattern_learning["fill_frequency"] = fill_count / len(all_commands)

    def _adapt_decisions(self, commands: List[DrumCommand], intent: IntentVector):
        """Adatta decisioni basato su apprendimento"""
        if self.pattern_learning["ghost_ratio"] > 0.3:
            for cmd in commands:
                if cmd.drum == DrumType.SNARE and not cmd.ghost:
                    if np.random.random() < 0.3:
                        cmd.ghost = True
                        cmd.velocity = int(cmd.velocity * 0.6)


def create_reactive_system(
    complexity: str = "medium", style: str = "rock"
) -> Tuple[RealtimeIntentProcessor, AdaptiveDecisionEngine]:
    """
    Crea il sistema reattivo completo.

    Args:
        complexity: Complessità
        style: Stile musicale

    Returns:
        Tuple (processor, engine)
    """
    config = DecisionConfig(complexity=complexity, style=style, humanize=0.5, swing=0.1)

    processor = RealtimeIntentProcessor()
    engine = AdaptiveDecisionEngine(config)

    return processor, engine


if __name__ == "__main__":
    print("=" * 60)
    print("DECISION ENGINE TEST")
    print("=" * 60)

    processor, engine = create_reactive_system("medium", "rock")

    for i in range(8):
        intent = processor.feed_beats(
            beat_time=i * 0.5,
            onsets=[i * 0.5] if i % 2 == 0 else [],
            energy=0.5 + 0.1 * np.sin(i * 0.3),
        )

        if i % 4 == 0:
            print(f"\n--- Bar {i // 4} ---")

        commands = engine.process_intent(intent)

        print(f"\nBeat {i}:")
        for cmd in commands:
            ghost_mark = " (ghost)" if cmd.ghost else ""
            print(f"  {cmd.drum.value}: vel={cmd.velocity}{ghost_mark}")

    print("\n[OK] Test completato")


if __name__ == "__main__":
    main()
