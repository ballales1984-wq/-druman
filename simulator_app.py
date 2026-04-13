"""
Simulatore App Batteria - Mostra tutti i calcoli di trigger, latenza e modulazione
in tempo reale o simulato
"""

import time
import random
import numpy as np
from src.trigger_system import TriggerSystem


class DrumSimulator:
    """Simulatore completo che mostra tutti i calcoli insieme"""

    def __init__(self):
        """Inizializza il simulatore"""
        self.trigger_system = TriggerSystem()
        self.running = False
        self.simulation_mode = "realtime"  # 'realtime' o 'simulated'
        self.frame_count = 0

    def print_header(self):
        """Stampa header del simulatore"""
        print("=" * 80)
        print("🥁 DRUM SIMULATOR - Menu Principale")

    print("=" * 80)
    print("\nScegli modalità:")
    print("1. Simulazione (10 frame, 1s delay)")
    print("2. Demo tempo reale (10s, 2 FPS)")
    print("3. Modalità interattiva (input manuale)")
    print("4. Generazione batteria da audio")
    print("5. Esci")
    print()

    drum_gen_app = DrumGeneratorApp()

    try:
        scelta = input("Scelta [1-5]: ").strip()

        if scelta == "1":
            simulator.run_simulation(num_frames=10, delay=1.0)
        elif scelta == "2":
            simulator.run_realtime_demo(duration=10.0, fps=2.0)
        elif scelta == "3":
            simulator.interactive_mode()
        elif scelta == "4":
            drum_gen_app.run()
        elif scelta == "5":
            print("\n👋 Arrivederci!\n")
        else:
            print("\n⚠️  Scelta non valida\n")

    except KeyboardInterrupt:
        print("\n\n👋 Arrivederci!\n")
    except Exception as e:
        print(f"\n\n❌ Errore: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
