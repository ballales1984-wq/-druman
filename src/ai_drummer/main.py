"""
Modulo Main - Orchestratore principale del sistema ReaperDrummerAI.
Coordina analyzer, drum_generator e humanizer per creare la batteria.
"""

import os
import sys
from typing import Optional, Dict, List
from pathlib import Path

import pretty_midi


try:
    from .analyzer import AudioAnalyzer, analyze_reference
    from .drum_generator import (
        DrumGenerator,
        generate_drum_pattern,
        Complexity,
        MusicStyle,
    )
    from .humanizer import Humanizer, humanize_midi, HumanGroove
    from .intent_vector import (
        IntentVector,
        IntentExtractor,
        RealtimeIntentProcessor,
        create_intent_from_analysis,
    )
    from .decision_engine import (
        DecisionEngine,
        AdaptiveDecisionEngine,
        DecisionConfig,
        create_reactive_system,
    )
except ImportError:
    from analyzer import AudioAnalyzer, analyze_reference
    from drum_generator import (
        DrumGenerator,
        generate_drum_pattern,
        Complexity,
        MusicStyle,
    )
    from humanizer import Humanizer, humanize_midi, HumanGroove
    from intent_vector import (
        IntentVector,
        IntentExtractor,
        RealtimeIntentProcessor,
        create_intent_from_analysis,
    )
    from decision_engine import (
        DecisionEngine,
        AdaptiveDecisionEngine,
        DecisionConfig,
        create_reactive_system,
    )


class ReaperDrummerAI:
    """Orchestratore principale - il cuore del sistema AI Drummer"""

    def __init__(self):
        self.analyzer = AudioAnalyzer()
        self.generator = DrumGenerator()
        self.humanizer = Humanizer()
        self.analysis_result = None
        self.generated_midi: Optional[pretty_midi.PrettyMIDI] = None

    def process(
        self,
        reference_audio: Optional[str] = None,
        length_bars: int = 8,
        complexity: str = "medium",
        style: str = "rock",
        apply_humanize: bool = True,
        swing: float = 0.0,
        output_dir: str = "outputs",
    ) -> Dict[str, str]:
        """
        Processa la traccia e genera la batteria.

        Args:
            reference_audio: Percorso della traccia audio di riferimento
            length_bars: Numero di battute
            complexity: Complessità (base, medium, advanced, expert)
            style: Stile musicale
            apply_humanize: Applica humanization
            swing: Quantità di swing
            output_dir: Directory per gli output

        Returns:
            Dict con paths dei file generati
        """
        os.makedirs(output_dir, exist_ok=True)

        output_files = {}

        base_name = Path(reference_audio).stem if reference_audio else "generated"

        print("\n" + "=" * 60)
        print("REAPER DRUMMER AI")
        print("=" * 60)

        if reference_audio and os.path.exists(reference_audio):
            print(f"\n[1/3] Analisi audio: {reference_audio}")
            self.analysis_result = self.analyzer.analyze(reference_audio)

            if self.analysis_result:
                self.generator.tempo = self.analysis_result.tempo

            print(f"\n[2/3] Estrazione groove...")
            groove = self.humanizer.extract_groove_from_audio(reference_audio)
            self.humanizer.set_groove(groove)
        else:
            print("[INFO] Nessun audio di riferimento, generazione base...")

        print(f"\n[2/3] Generazione pattern ({complexity}, {length_bars} battute)...")

        if self.analysis_result:
            self.generator.analysis = self.analysis_result

        self.generated_midi = self.generator.generate(
            length_bars=length_bars,
            complexity=complexity,
            style=style,
            use_analysis=bool(self.analysis_result),
        )

        output_base = os.path.join(output_dir, f"{base_name}_{complexity}.mid")
        self.generated_midi.write(output_base)
        output_files["base"] = output_base
        print(f"  - Base: {output_base}")

        if apply_humanize:
            print(f"\n[3/3] Humanization...")

            self.humanizer.set_groove(
                self.humanizer.groove or HumanGroove(humanize=0.5)
            )

            self.humanizer.apply_groove(self.generated_midi, 0.5)

            if swing > 0:
                self.humanizer.add_swing(self.generated_midi, swing)

            self.humanizer.vary_velocity(self.generated_midi, 0.1)

            if self.analysis_result and self.analysis_result.sections:
                self.humanizer.create_groove_automation(
                    self.generated_midi, self.analysis_result.sections
                )

            output_human = os.path.join(
                output_dir, f"{base_name}_{complexity}_humanized.mid"
            )
            self.generated_midi.write(output_human)
            output_files["humanized"] = output_human
            print(f"  - Humanized: {output_human}")

        self._print_summary()

        return output_files

    def generate_progressive(
        self,
        reference_audio: Optional[str] = None,
        length_bars: int = 8,
        style: str = "rock",
        output_dir: str = "outputs",
    ) -> Dict[str, str]:
        """
        Genera versioni progressive (base → expert).

        Args:
            reference_audio: Percorso audio
            length_bars: Numero battute
            style: Stile
            output_dir: Directory output

        Returns:
            Dict con path delle versioni
        """
        versions = ["base", "medium", "advanced"]

        print("\n" + "=" * 60)
        print("GENERAZIONE PROGRESSIVA")
        print("=" * 60)

        if reference_audio and os.path.exists(reference_audio):
            self.analysis_result = self.analyzer.analyze(reference_audio)
            self.generator.analysis = self.analysis_result

        output_files = {}

        for version in versions:
            midi = self.generator.generate(
                length_bars=length_bars,
                complexity=version,
                style=style,
                use_analysis=bool(self.analysis_result),
            )

            os.makedirs(output_dir, exist_ok=True)
            base_name = Path(reference_audio).stem if reference_audio else "drums"
            output_path = os.path.join(output_dir, f"{base_name}_{version}.mid")

            midi.write(output_path)
            output_files[version] = output_path

            print(f"[OK] {version}: {output_path}")

        return output_files

    def generate_evolution(
        self,
        reference_audio: Optional[str] = None,
        length_bars: int = 8,
        style: str = "rock",
        output_dir: str = "outputs",
        max_complexity: str = "expert",
    ) -> Dict[str, str]:
        """
        Genera evoluzione: parte semplice e evolve.

        Args:
            reference_audio: Percorso audio
            length_bars: Numero battute
            style: Stile
            output_dir: Directory output
            max_complexity: Complessità massima

        Returns:
            Dict con path delle versioni
        """
        complexity_levels = ["base", "medium", "advanced", "expert"]

        if max_complexity not in complexity_levels:
            max_complexity = "expert"

        max_idx = complexity_levels.index(max_complexity) + 1
        complexity_levels = complexity_levels[:max_idx]

        print("\n" + "=" * 60)
        print("EVOLUZIONE PATTERN")
        print("=" * 60)

        if reference_audio and os.path.exists(reference_audio):
            self.analysis_result = self.analyzer.analyze(reference_audio)
            self.generator.analysis = self.analysis_result

        output_files = {}

        for i, complexity in enumerate(complexity_levels):
            print(f"\n[Step {i + 1}/{len(complexity_levels)}] {complexity}...")

            midi = self.generator.generate(
                length_bars=length_bars,
                complexity=complexity,
                style=style,
                use_analysis=bool(self.analysis_result),
            )

            if complexity != "base":
                self.humanizer.apply_groove(
                    midi, (i + 1) / len(complexity_levels) * 0.6
                )
                self.humanizer.vary_velocity(
                    midi, (i + 1) / len(complexity_levels) * 0.1
                )

                if complexity in ["advanced", "expert"]:
                    self.humanizer.add_swing(midi, 0.1)

            os.makedirs(output_dir, exist_ok=True)
            base_name = Path(reference_audio).stem if reference_audio else "drums"
            output_path = os.path.join(
                output_dir, f"{base_name}_evolve_{complexity}.mid"
            )

            midi.write(output_path)
            output_files[complexity] = output_path

            notes_count = sum(
                len(inst.notes) for inst in midi.instruments if inst.is_drum
            )
            print(f"  - Note: {notes_count}")

        return output_files

    def generate_for_reaper(
        self,
        reference_audio: Optional[str] = None,
        length_bars: int = 32,
        style: str = "rock",
        output_dir: str = "outputs",
    ) -> str:
        """
        Genera un file MIDI ottimizzato per Reaper.
        Include tutte le versioni progressive.

        Args:
            reference_audio: Percorso audio
            length_bars: Numero battute
            style: Stile
            output_dir: Directory output

        Returns:
            Percorso del file principale
        """
        print("\n" + "=" * 60)
        print("GENERAZIONE PER REAPER")
        print("=" * 60)

        files = self.generate_progressive(
            reference_audio=reference_audio,
            length_bars=length_bars,
            style=style,
            output_dir=output_dir,
        )

        main_file = files.get("medium", list(files.values())[0])

        print(f"\n[OK] File principale: {main_file}")
        print("\nIstruzioni per Reaper:")
        print("  1. Trascina il MIDI su una traccia")
        print("  2. Aggiungi ReaSamplOmatic5000 come FX")
        print("  3. Carica i tuoi campioni di batteria")
        print("  4. Suona!")

        return main_file

    def run_reactive(
        self,
        reference_audio: Optional[str] = None,
        bars: int = 32,
        style: str = "rock",
        complexity: str = "medium",
        output_dir: str = "outputs",
    ) -> Dict[str, str]:
        """
        Esegue il sistema REATTIVO - il cuore del progetto.

        Questo è il sistema che:
        1. Estrae intent (cosa vuole il musicista)
        2. Decide (cosa suonare)
        3. Genera (comandi drum)

        Args:
            reference_audio: Percorso audio
            bars: Numero battute
            style: Stile musicale
            complexity: Complessità
            output_dir: Directory output

        Returns:
            Dict con path dei file generati
        """
        print("\n" + "=" * 60)
        print("REACTIVE AI DRUMMER SYSTEM")
        print("=" * 60)

        from .decision_engine import create_reactive_system, DecisionConfig
        from .intent_vector import create_intent_from_analysis

        os.makedirs(output_dir, exist_ok=True)

        if reference_audio and os.path.exists(reference_audio):
            print(f"\n[1/4] Analisi: {reference_audio}")
            self.analysis_result = self.analyzer.analyze(reference_audio)

            intent_data = self.analysis_result.to_dict() if self.analysis_result else {}
            intent = create_intent_from_analysis(intent_data)
        else:
            intent = create_intent_from_analysis({})
            intent.tempo = 120.0

        print(f"\n[2/4] Creazione sistema reattivo...")

        config = DecisionConfig(
            complexity=complexity, style=style, humanize=0.5, swing=0.1
        )

        processor, engine = create_reactive_system(complexity, style)

        print(f"\n[3/4] Generazione reattiva ({bars} battute)...")

        midi = engine.generate_midi(intent, bars)

        base_name = Path(reference_audio).stem if reference_audio else "reactive"
        output_path = os.path.join(output_dir, f"{base_name}_reactive.mid")

        midi.write(output_path)

        output_files = {"reactive": output_path}

        print(f"\n[4/4] Risultato:")
        total_notes = sum(len(inst.notes) for inst in midi.instruments if inst.is_drum)
        print(f"  - Note generate: {total_notes}")
        print(f"  - File: {output_path}")

        print("\n" + "-" * 60)
        print("SISTEMA REATTIVO ATTIVO")
        print("-" * 60)
        print(f"IntentVector:")
        print(f"  - Tempo: {intent.tempo:.1f} BPM")
        print(f"  - Kick prob: {intent.kick_probability:.2f}")
        print(f"  - Snare prob: {intent.snare_probability:.2f}")
        print(f"  - Groove: {intent.groove_type.value}")
        print(f"  - Intensity: {intent.current_intensity:.2f}")

        return output_files

    def _print_summary(self):
        """Stampa sommario"""
        if not self.generated_midi:
            return

        print("\n" + "-" * 60)
        print("SOMMARIO")
        print("-" * 60)

        for inst in self.generated_midi.instruments:
            if inst.is_drum:
                notes_by_pitch = {}
                for note in inst.notes:
                    pitch_name = pretty_midi.note_number_to_name(note.pitch)
                    notes_by_pitch[pitch_name] = notes_by_pitch.get(pitch_name, 0) + 1

                print(f"Note totali: {len(inst.notes)}")
                for pitch, count in sorted(notes_by_pitch.items()):
                    print(f"  - {pitch}: {count}")


def main():
    """Entry point da riga di comando"""
    if len(sys.argv) < 2:
        print("""
ReaperDrummerAI -Generatore Batteria AI

Usage: python -m src.ai_drummer.main <reference_audio> [options]

Options:
  --bars N         Numero battute (default: 8)
  --style STYLE   Stile: rock, pop, hiphop, electronic, jazz, metal, rnb, funk
  --complexity C   Complessità: base, medium, advanced, expert
  --progressive   Genera tutte le versioni progressive
  --evolution    Genera con evoluzione (base→expert)
  --no-humanize   Disabilita humanization
  --swing N       Quantità swing (0-1)
  --output DIR    Directory output

Examples:
  python -m src.ai_drummer.main my_song.wav --bars 16 --style rock --progressive
  python -m src.ai_drummer.main reference.wav --evolution --style hiphop
  python -m src.ai_drummer.main --style electronic --complexity base --no-humanize
        """)
        sys.exit(1)

    reference_audio = None
    args = sys.argv[1:]

    if args[0] and not args[0].startswith("--"):
        reference_audio = args[0]
        args = args[1:]

    length_bars = 8
    style = "rock"
    complexity = "medium"
    mode = "single"
    apply_humanize = True
    swing = 0.0
    output_dir = "outputs"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--bars" and i + 1 < len(args):
            length_bars = int(args[i + 1])
            i += 2
        elif arg == "--style" and i + 1 < len(args):
            style = args[i + 1]
            i += 2
        elif arg == "--complexity" and i + 1 < len(args):
            complexity = args[i + 1]
            i += 2
        elif arg == "--progressive":
            mode = "progressive"
            i += 1
        elif arg == "--evolution":
            mode = "evolution"
            i += 1
        elif arg == "--no-humanize":
            apply_humanize = False
            i += 1
        elif arg == "--swing" and i + 1 < len(args):
            swing = float(args[i + 1])
            i += 2
        elif arg == "--output" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        else:
            i += 1

    ai = ReaperDrummerAI()

    if mode == "progressive":
        ai.generate_progressive(
            reference_audio=reference_audio,
            length_bars=length_bars,
            style=style,
            output_dir=output_dir,
        )
    elif mode == "evolution":
        ai.generate_evolution(
            reference_audio=reference_audio,
            length_bars=length_bars,
            style=style,
            output_dir=output_dir,
        )
    else:
        ai.process(
            reference_audio=reference_audio,
            length_bars=length_bars,
            complexity=complexity,
            style=style,
            apply_humanize=apply_humanize,
            swing=swing,
            output_dir=output_dir,
        )


if __name__ == "__main__":
    main()
