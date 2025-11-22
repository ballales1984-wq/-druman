"""
Gestore Libreria Suoni - Avvia l'interfaccia per gestire la libreria
"""
import sys
import os

# Aggiungi percorso progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.sound_library_ui import main
    
    if __name__ == "__main__":
        print("=" * 60)
        print("DrumMan - Gestore Libreria Suoni")
        print("=" * 60)
        print()
        main()
        
except ImportError as e:
    print(f"❌ Errore importazione: {e}")
    print("\nAssicurati di aver installato tutte le dipendenze:")
    print("  pip install soundfile")
    input("\nPremi Enter per uscire...")

