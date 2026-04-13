"""
DrumMan AI Generator - Simple UI

Interfaccia semplice per generare batterie da file audio.
"""

import os
import sys
from pathlib import Path


def print_header():
    print("=" * 60)
    print("     DRUMMAN AI - Generatore Batteria Automatica")
    print("=" * 60)
    print()


def print_menu():
    print("Scegli un'opzione:")
    print()
    print("  1. Genera da file audio")
    print("  2. Genera con parametri manuali")
    print("  3. Prova esempio")
    print("  4. Esci")
    print()


def get_file_path() -> str:
    """Richiede percorso file audio"""
    print("\nInserisci percorso del file audio (mp3, wav, flac):")
    print("  (lascia vuoto per annullare)")
    path = input("\n> ").strip().strip('"')

    if not path:
        return None

    if not os.path.exists(path):
        print(f"\nERRORE: File non trovato: {path}")
        return None

    return path


def get_style() -> str:
    """Richiede stile musicale"""
    print("\nScegli stile:")
    print("  1. Rock")
    print("  2. Pop")
    print("  3. Hip-Hop")
    print("  4. Electronic")
    print("  5. Jazz")
    print("  6. Metal")
    print("  7. R&B")
    print("  8. Auto (rilevamento automatico)")

    choice = input("\n> ").strip()

    styles = {
        "1": "rock",
        "2": "pop",
        "3": "hiphop",
        "4": "electronic",
        "5": "jazz",
        "6": "metal",
        "7": "rnb",
        "8": "auto",
    }

    return styles.get(choice, "rock")


def get_bars() -> int:
    """Richiede numero battute"""
    print("\nNumero battute (default 8):")
    bars = input("\n> ").strip()

    try:
        return int(bars) if bars else 8
    except:
        return 8


def get_complexity() -> str:
    """Richiede complessità"""
    print("\nComplessità:")
    print("  1. Simple (base)")
    print("  2. Medium (medio)")
    print("  3. Complex (avanzato)")

    choice = input("\n> ").strip()

    complexities = {"1": "simple", "2": "medium", "3": "complex"}
    return complexities.get(choice, "medium")


def generate_from_audio(audio_path: str, style: str, bars: int, complexity: str):
    """Genera da file audio"""
    print(f"\n{'=' * 60}")
    print(f"Generazione da: {audio_path}")
    print(f"Stile: {style}, Battute: {bars}, Complessità: {complexity}")
    print(f"{'=' * 60}")

    try:
        from src.drum_generator import DrumGenerator, MusicStyle, analyze_and_generate

        print("\n[1/3] Analisi audio...")

        # Map style
        style_map = {
            "rock": MusicStyle.ROCK,
            "pop": MusicStyle.POP,
            "hiphop": MusicStyle.HIPHOP,
            "electronic": MusicStyle.ELECTRONIC,
            "jazz": MusicStyle.JAZZ,
            "metal": MusicStyle.METAL,
            "rnb": MusicStyle.RNB,
            "auto": None,
        }
        style_enum = style_map.get(style, MusicStyle.ROCK)

        print("\n[2/3] Generazione pattern...")

        # Generate
        generator = DrumGenerator()
        audio, duration = generator.load_audio(audio_path)
        analysis = generator.analyze_audio(audio)
        pattern = generator.generate_drum_pattern(
            bars=bars, style=style_enum, complexity=complexity
        )

        # Determine output filename
        base_name = Path(audio_path).stem
        output_path = f"outputs/{base_name}_drums.mid"
        os.makedirs("outputs", exist_ok=True)

        print("\n[3/3] Esportazione...")
        generator.export_to_midi(output_path)

        print(f"\n{'=' * 60}")
        print("Fatto!")
        print(f"File: {output_path}")
        print(generator.get_pattern_summary())
        print(f"{'=' * 60}")

        return output_path

    except Exception as e:
        print(f"\nERRORE: {e}")
        import traceback

        traceback.print_exc()
        return None


def generate_manual(style: str, bars: int, complexity: str):
    """Genera con parametri manuali"""
    print(f"\n{'=' * 60}")
    print(f"Generazione: Stile={style}, Battute={bars}, Complessità={complexity}")
    print(f"{'=' * 60}")

    try:
        from src.drum_generator import DrumGenerator, MusicStyle

        style_map = {
            "rock": MusicStyle.ROCK,
            "pop": MusicStyle.POP,
            "hiphop": MusicStyle.HIPHOP,
            "electronic": MusicStyle.ELECTRONIC,
            "jazz": MusicStyle.JAZZ,
            "metal": MusicStyle.METAL,
            "rnb": MusicStyle.RNB,
            "auto": None,
        }
        style_enum = style_map.get(style, MusicStyle.ROCK)

        gen = DrumGenerator()

        # Set minimal analysis
        class MinimalAnalysis:
            tempo = 120.0
            time_signature = (4, 4)
            style = style_enum
            duration = bars * 4 * (60 / 120)
            key = None
            energy = 0.5
            beat_positions = []

        gen.analysis = MinimalAnalysis()

        pattern = gen.generate_drum_pattern(bars=bars, complexity=complexity)

        output_path = f"outputs/manual_{style}_{bars}bar.mid"
        os.makedirs("outputs", exist_ok=True)
        gen.export_to_midi(output_path)

        print(f"\nFatto!")
        print(f"File: {output_path}")
        print(gen.get_pattern_summary())

        return output_path

    except Exception as e:
        print(f"\nERRORE: {e}")
        return None


def run_example():
    """Genera esempio predefinito"""
    print("\nGenerazione esempio Rock...")
    return generate_manual("rock", bars=8, complexity="medium")


def main():
    """Main loop"""
    print_header()

    while True:
        print_menu()
        choice = input("Scelta > ").strip()

        if choice == "1":
            # Generate from audio file
            audio_path = get_file_path()
            if not audio_path:
                continue

            style = get_style()
            bars = get_bars()
            complexity = get_complexity()

            output = generate_from_audio(audio_path, style, bars, complexity)

            if output:
                print(f"\n✓ File pronto: {output}")
                print("Importalo in Reaper!")

        elif choice == "2":
            # Generate with manual params
            style = get_style()
            bars = get_bars()
            complexity = get_complexity()

            output = generate_manual(style, bars, complexity)

            if output:
                print(f"\n✓ File pronto: {output}")

        elif choice == "3":
            # Example
            output = run_example()
            if output:
                print(f"\n✓ Esempio pronto: {output}")

        elif choice == "4" or choice.lower() in ["exit", "quit", "esci"]:
            print("\nCiao!")
            break

        else:
            print("\nScelta non valida")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DrumMan AI Generator")
    parser.add_argument("--audio", "-a", help="Audio file path")
    parser.add_argument(
        "--style",
        "-s",
        default="rock",
        help="Style: rock, pop, hiphop, electronic, jazz, metal, rnb",
    )
    parser.add_argument("--bars", "-b", type=int, default=8, help="Number of bars")
    parser.add_argument(
        "--complexity",
        "-c",
        default="medium",
        help="Complexity: simple, medium, complex",
    )
    parser.add_argument(
        "--example", "-e", action="store_true", help="Run example and exit"
    )
    args = parser.parse_args()

    if args.example or args.audio:
        # Run in batch mode
        if args.audio:
            generate_from_audio(args.audio, args.style, args.bars, args.complexity)
        else:
            generate_manual(args.style, args.bars, args.complexity)
    else:
        # Interactive mode
        main()
