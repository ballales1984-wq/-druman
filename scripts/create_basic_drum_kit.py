"""
Crea un kit di suoni base usando la sintesi
Utile se non si hanno file audio esterni
"""
import numpy as np
import sys
import os
from pathlib import Path

# Aggiungi percorso progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("⚠️  soundfile non installato. Installa con: pip install soundfile")
    sys.exit(1)

from src.drum_machine import DrumMachine


def generate_kit_samples():
    """Genera campioni usando la sintesi della drum machine"""
    print("="*60)
    print("Generazione Kit Suoni Base")
    print("="*60)
    print()
    
    # Crea directory
    sounds_dir = Path("sounds/kits/basic_synthesized")
    sounds_dir.mkdir(parents=True, exist_ok=True)
    
    # Crea drum machine
    drum_machine = DrumMachine(sample_rate=44100)
    
    # Genera tutti i suoni
    components = ['kick', 'snare', 'hihat', 'crash', 'tom1', 'tom2']
    
    print("Generazione campioni...")
    for component in components:
        if component in drum_machine.sounds:
            audio = drum_machine.sounds[component]
            file_path = sounds_dir / f"{component}.wav"
            
            # Converti a stereo se necessario
            if len(audio.shape) == 1:
                audio_stereo = np.column_stack([audio, audio])
            else:
                audio_stereo = audio
            
            # Salva
            sf.write(str(file_path), audio_stereo, 44100)
            print(f"  [OK] {component}.wav ({len(audio)/44100:.2f}s)")
    
    print(f"\n[OK] Kit generato in: {sounds_dir}")
    print(f"   Totale file: {len(components)}")
    
    return sounds_dir


def main():
    """Funzione principale"""
    if not SOUNDFILE_AVAILABLE:
        print("❌ soundfile non disponibile!")
        return
    
    kit_dir = generate_kit_samples()
    
    print("\n" + "="*60)
    print("Prossimi passi:")
    print("="*60)
    print("1. Apri sound_library_manager.py")
    print("2. Carica Cartella e seleziona:", kit_dir)
    print("3. I suoni verranno caricati automaticamente")
    print("4. Modifica i parametri a piacimento")
    print("5. Salva un preset")
    print()


if __name__ == "__main__":
    main()

