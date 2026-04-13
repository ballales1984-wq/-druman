"""
Modulo UI - Interfaccia Utente

Interfaccia semplice e intuitiva per il sistema AI Drummer.
Supporta:
- CLI interattiva
- UI semplice con curses
- Web UI basic
"""

import os
import sys
import time
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class UIConfig:
    """Configurazione UI"""

    theme: str = "dark"
    color_output: bool = True
    show_waveform: bool = True
    bpm_display: bool = True


class SimpleCLI:
    """
    CLI interattiva semplice.
    """

    def __init__(self, config: Optional[UIConfig] = None):
        self.config = config or UIConfig()
        self.running = False

    def clear_screen(self):
        """Pulisce schermo"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, title: str):
        """Stampa header"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_menu(self, options: List[str], title: str = "Menu"):
        """Stampa menu"""
        self.print_header(title)
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        print()

    def get_choice(self, max_val: int) -> int:
        """Ottiene scelta"""
        while True:
            try:
                choice = input("  Scelta: ").strip()
                val = int(choice)
                if 1 <= val <= max_val:
                    return val
            except:
                pass

    def show_progress(self, current: int, total: int, label: str = ""):
        """Mostra progresso"""
        pct = current / total
        bar = "█" * int(pct * 20) + "░" * (20 - int(pct * 20))
        print(f"\r  [{bar}] {pct * 100:.0f}% {label}", end="")
        if current == total:
            print()

    def show_analysis(self, data: Dict):
        """Mostra analisi"""
        print("\n  📊 Analisi:")
        print(f"     BPM: {data.get('tempo', 120):.1f}")
        print(f"     Beat: {data.get('beats', 0)}")
        print(f"     Onsets: {data.get('onsets', 0)}")
        print(f"     Sezioni: {data.get('sections', 0)}")

    def show_intent(self, intent: Dict):
        """Mostra intent"""
        print("\n  🎯 Intent:")
        print(f"     Kick prob: {intent.get('kick_probability', 0):.2f}")
        print(f"     Snare prob: {intent.get('snare_probability', 0):.2f}")
        print(f"     Groove: {intent.get('groove_type', 'straight')}")
        print(f"     Intensity: {intent.get('current_intensity', 0):.2f}")

    def show_generation(self, events: int, bars: int):
        """Mostra generazione"""
        print(f"\n  🥁 Generato:")
        print(f"     Eventi: {events}")
        print(f"     Battute: {bars}")

    def prompt_file(self, label: str = "File") -> str:
        """Prompt per file"""
        path = input(f"  {label} [Enter per skip]: ").strip()
        return path


class DrummerUI:
    """
    UI principale per AI Drummer.
    """

    def __init__(self):
        self.cli = SimpleCLI()
        self.generator = None

    def run(self):
        """Esegue UI"""
        self.cli.running = True

        while self.cli.running:
            self.cli.print_menu(
                [
                    "Genera da file audio",
                    "Genera con sistema reattivo",
                    "Generazione progressiva",
                    "Integrazione Reaper",
                    "Impostazioni",
                    "Esci",
                ],
                "AI DRUMMER",
            )

            choice = self.cli.get_choice(6)

            if choice == 1:
                self._generate_from_file()
            elif choice == 2:
                self._generate_reactive()
            elif choice == 3:
                self._generate_progressive()
            elif choice == 4:
                self._reaper_integration()
            elif choice == 5:
                self._settings()
            elif choice == 6:
                self.cli.running = False
                print("\n👋 Ciao!\n")

    def _generate_from_file(self):
        """Genera da file"""
        self.cli.print_header("Genera da Audio")

        path = self.cli.prompt_file("File audio")
        if not path:
            return

        if not os.path.exists(path):
            print(f"[ERR] File non trovato")
            return

        # Opzioni
        print("\n  Stile:")
        print("  1. Rock")
        print("  2. Hiphop")
        print("  3. Electronic")
        print("  4. Jazz")

        style_map = {1: "rock", 2: "hiphop", 3: "electronic", 4: "jazz"}
        style = style_map.get(self.cli.get_choice(4), "rock")

        # Genera
        print("\n[INFO] Generazione...")

        try:
            from .main import ReaperDrummerAI

            ai = ReaperDrummerAI()
            files = ai.process(
                reference_audio=path, length_bars=8, complexity="medium", style=style
            )

            print(f"\n[OK] Generato: {list(files.values())}")

        except Exception as e:
            print(f"[ERR] {e}")

    def _generate_reactive(self):
        """Sistema reattivo"""
        self.cli.print_header("Sistema Reattivo")

        path = self.cli.prompt_file("File audio (opzionale)")

        try:
            from .main import ReaperDrummerAI

            ai = ReaperDrummerAI()
            files = ai.run_reactive(
                reference_audio=path if path and os.path.exists(path) else None,
                bars=16,
                style="rock",
            )

            print(f"\n[OK] {list(files.values())}")

        except Exception as e:
            print(f"[ERR] {e}")

    def _generate_progressive(self):
        """Generazione progressiva"""
        self.cli.print_header("Generazione Progressiva")

        path = self.cli.prompt_file("File audio")

        try:
            from .main import ReaperDrummerAI

            ai = ReaperDrummerAI()
            files = ai.generate_progressive(
                reference_audio=path if path and os.path.exists(path) else None,
                length_bars=8,
                style="rock",
            )

            print("\n[OK] Versioni:")
            for ver, f in files.items():
                print(f"  - {ver}: {f}")

        except Exception as e:
            print(f"[ERR] {e}")

    def _reaper_integration(self):
        """Integrazione Reaper"""
        self.cli.print_header("Integrazione Reaper")

        print("\n  1. Inserisci MIDI esistente")
        print("  2. Genera e inserisci")

        try:
            from .reaper_integration import create_reaper_session

            if self.cli.get_choice(2) == 1:
                midi = self.cli.prompt_file("File MIDI")
                if midi and os.path.exists(midi):
                    create_reaper_session(midi)
            else:
                print("[INFO] Genera prima, poi inserisci")

        except Exception as e:
            print(f"[ERR] {e}")

    def _settings(self):
        """Impostazioni"""
        self.cli.print_header("Impostazioni")

        print("\n  Complessità:")
        print("  1. Base")
        print("  2. Medium")
        print("  3. Advanced")
        print("  4. Expert")

        print("\n  Torna al menu principale")


def run_ui():
    """Entry point UI"""
    ui = DrummerUI()
    ui.run()


if __name__ == "__main__":
    run_ui()
