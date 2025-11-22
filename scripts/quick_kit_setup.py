"""
Setup Rapido Kit Suoni - Crea kit base e configura tutto
"""
import os
import sys
from pathlib import Path

# Aggiungi percorso progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Setup rapido"""
    print("="*60)
    print("DrumMan - Quick Kit Setup")
    print("="*60)
    print()
    
    # 1. Genera kit sintetizzato
    print("1. Generazione kit base sintetizzato...")
    try:
        from scripts.create_basic_drum_kit import generate_kit_samples
        kit_dir = generate_kit_samples()
        print(f"   ✓ Kit creato in: {kit_dir}\n")
    except Exception as e:
        print(f"   ⚠️  Errore: {e}\n")
    
    # 2. Carica nella libreria
    print("2. Caricamento nella libreria...")
    try:
        from src.sound_library import SoundLibrary
        
        library = SoundLibrary("sounds")
        
        # Carica campioni dal kit
        kit_path = Path("sounds/kits/basic_synthesized")
        if kit_path.exists():
            mapping = {
                'kick': 'kick',
                'snare': 'snare',
                'hihat': 'hihat',
                'crash': 'crash',
                'tom1': 'tom1',
                'tom2': 'tom2'
            }
            
            library.import_samples_from_folder(str(kit_path), mapping)
            print("   ✓ Campioni caricati nella libreria\n")
        else:
            print("   ⚠️  Kit non trovato\n")
            
    except Exception as e:
        print(f"   ⚠️  Errore: {e}\n")
    
    # 3. Istruzioni
    print("="*60)
    print("Setup Completato!")
    print("="*60)
    print()
    print("Prossimi passi:")
    print("1. Apri sound_library_manager.py per modificare i suoni")
    print("2. Oppure modifica src/config.py:")
    print("   USE_SOUND_LIBRARY = True")
    print("3. Avvia DrumMan: python main.py")
    print()
    print("Per aggiungere più suoni:")
    print("  - Usa sound_library_manager.py → Carica File/Cartella")
    print("  - Oppure metti file WAV in sounds/kits/")
    print()


if __name__ == "__main__":
    main()

