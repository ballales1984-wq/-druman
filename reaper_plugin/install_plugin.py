"""
Script di installazione per il plugin DrumMan in Reaper
"""
import os
import sys
import shutil
from pathlib import Path

def find_reaper_scripts_dir():
    """Trova la directory Scripts di Reaper"""
    possible_paths = []
    
    # Windows
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA")
        if appdata:
            possible_paths.append(os.path.join(appdata, "REAPER", "Scripts"))
    
    # macOS
    elif sys.platform == "darwin":
        home = os.path.expanduser("~")
        possible_paths.append(os.path.join(home, "Library", "Application Support", "REAPER", "Scripts"))
    
    # Linux
    else:
        home = os.path.expanduser("~")
        possible_paths.append(os.path.join(home, ".config", "REAPER", "Scripts"))
    
    # Cerca directory esistente
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Se non trovata, chiedi all'utente
    return None

def install_plugin():
    """Installa il plugin in Reaper"""
    print("=" * 60)
    print("DrumMan Reaper Plugin - Installazione")
    print("=" * 60)
    print()
    
    # Trova directory Reaper
    reaper_scripts = find_reaper_scripts_dir()
    
    if not reaper_scripts:
        print("⚠️  Directory Scripts di Reaper non trovata automaticamente.")
        print()
        reaper_scripts = input("Inserisci il percorso completo della directory Scripts di Reaper: ").strip()
        
        if not os.path.exists(reaper_scripts):
            print(f"❌ Directory non trovata: {reaper_scripts}")
            return False
    
    print(f"✓ Directory Reaper trovata: {reaper_scripts}")
    print()
    
    # Percorso file plugin
    current_dir = Path(__file__).parent
    plugin_file = current_dir / "DrumMan_Reaper_Plugin.py"
    
    if not plugin_file.exists():
        print(f"❌ File plugin non trovato: {plugin_file}")
        return False
    
    # Copia file
    try:
        dest_file = os.path.join(reaper_scripts, "DrumMan_Reaper_Plugin.py")
        shutil.copy2(plugin_file, dest_file)
        print(f"✅ Plugin installato: {dest_file}")
        print()
        print("Prossimi passi:")
        print("1. Apri Reaper")
        print("2. Vai su Actions → Show action list")
        print("3. Clicca 'Load ReaScript'")
        print("4. Seleziona 'DrumMan_Reaper_Plugin.py'")
        print("5. Assegna una shortcut (es. Ctrl+Alt+D)")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Errore durante l'installazione: {e}")
        return False

if __name__ == "__main__":
    success = install_plugin()
    if success:
        print("✅ Installazione completata!")
    else:
        print("❌ Installazione fallita!")
    
    input("\nPremi Enter per uscire...")

