"""
Script principale per scaricare e configurare kit di suoni
Scarica kit reali da fonti online e genera kit sintetizzato come fallback
"""
import os
import sys
import urllib.request
import zipfile
import json
from pathlib import Path
import shutil

# Aggiungi percorso progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import soundfile as sf
    import numpy as np
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("[WARN] soundfile non installato. Installa con: pip install soundfile")

# Fonti kit gratuiti (URL diretti o repository)
DRUM_KIT_SOURCES = [
    {
        'name': 'Basic Synthesized Kit',
        'type': 'synthesized',
        'description': 'Kit generato con sintesi (sempre disponibile)'
    },
    {
        'name': 'FreeDrumKit Samples',
        'type': 'url',
        'url': 'https://github.com/free-samples/free-drum-samples/archive/refs/heads/main.zip',
        'description': 'Kit base gratuito da GitHub',
        'license': 'CC0'
    }
]


def generate_synthesized_kit(output_dir: Path):
    """Genera kit sintetizzato usando la drum machine"""
    if not SOUNDFILE_AVAILABLE:
        print("[ERROR] soundfile non disponibile per generare kit sintetizzato")
        return False
    
    print("Generazione kit sintetizzato...")
    
    try:
        from src.drum_machine import DrumMachine
        
        # Crea drum machine
        drum_machine = DrumMachine(sample_rate=44100)
        
        # Genera tutti i suoni
        components = ['kick', 'snare', 'hihat', 'crash', 'tom1', 'tom2']
        generated = 0
        
        for component in components:
            if component in drum_machine.sounds:
                audio = drum_machine.sounds[component]
                file_path = output_dir / f"{component}.wav"
                
                # Converti a stereo se necessario
                if len(audio.shape) == 1:
                    audio_stereo = np.column_stack([audio, audio])
                else:
                    audio_stereo = audio
                
                # Salva
                sf.write(str(file_path), audio_stereo, 44100)
                generated += 1
                print(f"  [OK] {component}.wav ({len(audio)/44100:.2f}s)")
        
        print(f"[OK] Kit sintetizzato generato: {generated} file")
        return True
        
    except Exception as e:
        print(f"[ERROR] Errore generazione kit: {e}")
        return False


def download_kit_from_url(url: str, output_dir: Path) -> bool:
    """Scarica un kit da URL"""
    try:
        print(f"Scaricamento da: {url}")
        
        # Crea directory temporanea
        temp_dir = output_dir.parent / "temp_download"
        temp_dir.mkdir(exist_ok=True)
        
        zip_file = temp_dir / "kit.zip"
        
        # Download con progresso
        def show_progress(count, block_size, total_size):
            if total_size > 0:
                percent = min(100, int(count * block_size * 100 / total_size))
                print(f"\r   Progresso: {percent}%", end='', flush=True)
        
        urllib.request.urlretrieve(url, zip_file, show_progress)
        print("\n[OK] Download completato!")
        
        # Estrai
        print("Estrazione...")
        extract_dir = temp_dir / "extracted"
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Trova file audio
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.aiff']
        audio_files = []
        for ext in audio_extensions:
            audio_files.extend(extract_dir.rglob(f'*{ext}'))
            audio_files.extend(extract_dir.rglob(f'*{ext.upper()}'))
        
        if not audio_files:
            print("[WARN] Nessun file audio trovato nel kit")
            shutil.rmtree(temp_dir)
            return False
        
        print(f"   Trovati {len(audio_files)} file audio")
        
        # Mappatura nomi file -> componenti batteria
        name_mapping = {
            'kick': ['kick', 'bass', 'bd', 'bassdrum', 'kickdrum'],
            'snare': ['snare', 'sn', 'sd', 'snaredrum'],
            'hihat': ['hihat', 'hh', 'hi-hat', 'hat', 'hi_hat'],
            'crash': ['crash', 'cr', 'crashcymbal'],
            'tom1': ['tom1', 'tom', 'tom-low', 'low-tom', 'lowtom'],
            'tom2': ['tom2', 'tom-high', 'high-tom', 'hightom']
        }
        
        # Organizza file
        organized = {}
        for audio_file in audio_files:
            file_name_lower = audio_file.stem.lower()
            
            # Cerca corrispondenza
            assigned = False
            for component, keywords in name_mapping.items():
                if any(keyword in file_name_lower for keyword in keywords):
                    # Copia file
                    dest_file = output_dir / f"{component}_{audio_file.name}"
                    shutil.copy2(audio_file, dest_file)
                    
                    if component not in organized:
                        organized[component] = []
                    organized[component].append(str(dest_file))
                    assigned = True
                    break
            
            if not assigned:
                # File non riconosciuto, copia comunque
                dest_file = output_dir / audio_file.name
                shutil.copy2(audio_file, dest_file)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        print(f"[OK] Kit organizzato: {len(organized)} componenti")
        return True
        
    except Exception as e:
        print(f"[ERROR] Errore download: {e}")
        return False


def setup_drum_kits():
    """Setup principale: scarica e configura tutti i kit"""
    print("="*60)
    print("DrumMan - Setup Kit Suoni")
    print("="*60)
    print()
    
    # Crea directory
    sounds_dir = Path("sounds")
    sounds_dir.mkdir(exist_ok=True)
    
    kits_dir = sounds_dir / "kits"
    kits_dir.mkdir(exist_ok=True)
    
    # 1. Genera sempre kit sintetizzato (fallback)
    synthesized_dir = kits_dir / "synthesized"
    synthesized_dir.mkdir(exist_ok=True)
    
    if not list(synthesized_dir.glob("*.wav")):
        if generate_synthesized_kit(synthesized_dir):
            print()
    else:
        print("[OK] Kit sintetizzato già presente\n")
    
    # 2. Prova a scaricare kit online
    print("="*60)
    print("Download Kit Online")
    print("="*60)
    print()
    
    downloaded = False
    
    for kit_source in DRUM_KIT_SOURCES:
        if kit_source['type'] == 'url':
            kit_name = kit_source['name'].lower().replace(' ', '_')
            kit_dir = kits_dir / kit_name
            kit_dir.mkdir(exist_ok=True)
            
            # Controlla se già scaricato
            if list(kit_dir.glob("*.wav")) or list(kit_dir.glob("*.mp3")):
                print(f"[OK] Kit '{kit_source['name']}' già presente")
                continue
            
            print(f"Tentativo download: {kit_source['name']}")
            if download_kit_from_url(kit_source['url'], kit_dir):
                downloaded = True
                print()
            else:
                print("[WARN] Download fallito, continuo...\n")
    
    if not downloaded:
        print("[WARN] Nessun kit online scaricato (usa kit sintetizzato)")
    
    # 3. Carica nella libreria
    print("="*60)
    print("Caricamento nella Libreria")
    print("="*60)
    print()
    
    try:
        from src.sound_library import SoundLibrary
        
        library = SoundLibrary(str(sounds_dir))
        
        # Carica dal kit sintetizzato (sempre disponibile)
        synthesized_path = synthesized_dir
        if synthesized_path.exists():
            mapping = {
                'kick': 'kick',
                'snare': 'snare',
                'hihat': 'hihat',
                'crash': 'crash',
                'tom1': 'tom1',
                'tom2': 'tom2'
            }
            
            library.import_samples_from_folder(str(synthesized_path), mapping)
            print("[OK] Kit sintetizzato caricato nella libreria")
        
        print()
        print("="*60)
        print("Setup Completato!")
        print("="*60)
        print()
        print("Kit disponibili:")
        for kit_dir in kits_dir.iterdir():
            if kit_dir.is_dir():
                files = list(kit_dir.glob("*.wav")) + list(kit_dir.glob("*.mp3"))
                if files:
                    print(f"  - {kit_dir.name}: {len(files)} file")
        print()
        print("Prossimi passi:")
        print("1. Avvia DrumMan: python main.py")
        print("2. Oppure modifica suoni con: python -m src.sound_library_ui")
        print()
        
    except ImportError as e:
        print(f"[WARN] SoundLibrary non disponibile: {e}")
        print("   I file sono stati scaricati in sounds/kits/")
        print("   Puoi caricarli manualmente")


def main():
    """Funzione principale"""
    setup_drum_kits()


if __name__ == "__main__":
    main()

