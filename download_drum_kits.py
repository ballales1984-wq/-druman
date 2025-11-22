"""
Script per scaricare kit di suoni di batteria gratuiti
e integrarli automaticamente in DrumMan
"""
import os
import sys
import urllib.request
import zipfile
import json
from pathlib import Path
import shutil

# Kit di suoni gratuiti disponibili
DRUM_KITS = {
    'free_drum_kit_1': {
        'name': 'FreeDrumKit - Basic',
        'url': 'https://github.com/free-samples/free-drum-samples/archive/refs/heads/main.zip',
        'description': 'Kit base con suoni essenziali',
        'license': 'CC0'
    },
    'matt_mcguire': {
        'name': 'Matt McGuire Free Drum Samples',
        'url': 'https://www.mattmcguire.net/samples/MattMcGuireDrumSamples.zip',
        'description': 'Kit professionale gratuito',
        'license': 'Free for personal use'
    }
}

# Alternative: Kit da Freesound.org (richiede API key)
FREESOUND_KITS = {
    'freesound_drum_kit': {
        'name': 'Freesound Drum Samples',
        'base_url': 'https://freesound.org',
        'description': 'Raccolta da Freesound.org',
        'license': 'CC'
    }
}

# Kit locali da creare (se non disponibili online)
LOCAL_KIT_PATHS = []


class DrumKitDownloader:
    """Classe per scaricare e installare kit di suoni"""
    
    def __init__(self, sounds_dir: str = "sounds"):
        """
        Inizializza il downloader
        
        Args:
            sounds_dir: Directory dove salvare i suoni
        """
        self.sounds_dir = Path(sounds_dir)
        self.sounds_dir.mkdir(exist_ok=True)
        
        self.kits_dir = self.sounds_dir / "kits"
        self.kits_dir.mkdir(exist_ok=True)
    
    def download_file(self, url: str, dest_path: Path, show_progress: bool = True) -> bool:
        """
        Scarica un file da URL
        
        Args:
            url: URL del file
            dest_path: Percorso destinazione
            show_progress: Mostra progresso
        
        Returns:
            True se scaricato con successo
        """
        try:
            if show_progress:
                print(f"📥 Scaricamento: {url}")
                print(f"   → {dest_path}")
            
            def show_progress_hook(count, block_size, total_size):
                if total_size > 0:
                    percent = min(100, int(count * block_size * 100 / total_size))
                    print(f"\r   Progresso: {percent}%", end='', flush=True)
            
            urllib.request.urlretrieve(url, dest_path, show_progress_hook if show_progress else None)
            
            if show_progress:
                print("\n✅ Download completato!")
            
            return True
        except Exception as e:
            print(f"\n❌ Errore download: {e}")
            return False
    
    def extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        """
        Estrae un file ZIP
        
        Args:
            zip_path: Percorso file ZIP
            extract_to: Directory destinazione
        
        Returns:
            True se estratto con successo
        """
        try:
            print(f"📦 Estrazione: {zip_path.name}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print("✅ Estrazione completata!")
            return True
        except Exception as e:
            print(f"❌ Errore estrazione: {e}")
            return False
    
    def find_audio_files(self, directory: Path) -> list:
        """
        Trova tutti i file audio in una directory
        
        Args:
            directory: Directory da cercare
        
        Returns:
            Lista di percorsi file audio
        """
        audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.aiff']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(directory.rglob(f'*{ext}'))
            audio_files.extend(directory.rglob(f'*{ext.upper()}'))
        
        return audio_files
    
    def organize_samples(self, source_dir: Path, kit_name: str):
        """
        Organizza i campioni scaricati
        
        Args:
            source_dir: Directory sorgente
            kit_name: Nome del kit
        """
        print(f"📁 Organizzazione campioni: {kit_name}")
        
        audio_files = self.find_audio_files(source_dir)
        
        if not audio_files:
            print("⚠️  Nessun file audio trovato")
            return
        
        print(f"   Trovati {len(audio_files)} file audio")
        
        # Crea directory per il kit
        kit_dir = self.kits_dir / kit_name
        kit_dir.mkdir(exist_ok=True)
        
        # Mappatura nomi file -> componenti batteria
        name_mapping = {
            'kick': ['kick', 'bass', 'bd', 'bassdrum'],
            'snare': ['snare', 'sn', 'sd'],
            'hihat': ['hihat', 'hh', 'hi-hat', 'hat'],
            'crash': ['crash', 'cr'],
            'tom1': ['tom1', 'tom', 'tom-low', 'low-tom'],
            'tom2': ['tom2', 'tom-high', 'high-tom']
        }
        
        organized = {}
        
        for audio_file in audio_files:
            file_name_lower = audio_file.stem.lower()
            
            # Cerca corrispondenza
            assigned = False
            for component, keywords in name_mapping.items():
                if any(keyword in file_name_lower for keyword in keywords):
                    # Copia file nella directory del kit
                    dest_file = kit_dir / f"{component}_{audio_file.name}"
                    shutil.copy2(audio_file, dest_file)
                    
                    if component not in organized:
                        organized[component] = []
                    organized[component].append(str(dest_file))
                    assigned = True
                    break
            
            if not assigned:
                # File non riconosciuto, copia comunque
                dest_file = kit_dir / audio_file.name
                shutil.copy2(audio_file, dest_file)
        
        # Salva metadata del kit
        metadata = {
            'name': kit_name,
            'samples': organized,
            'total_files': len(audio_files),
            'organized': len(organized)
        }
        
        metadata_file = kit_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Kit organizzato: {len(organized)} componenti")
    
    def download_kit(self, kit_id: str) -> bool:
        """
        Scarica e installa un kit
        
        Args:
            kit_id: ID del kit da DRUM_KITS
        
        Returns:
            True se installato con successo
        """
        if kit_id not in DRUM_KITS:
            print(f"❌ Kit '{kit_id}' non trovato")
            return False
        
        kit_info = DRUM_KITS[kit_id]
        print(f"\n{'='*60}")
        print(f"Scaricamento Kit: {kit_info['name']}")
        print(f"{'='*60}\n")
        
        # Crea directory temporanea
        temp_dir = self.kits_dir / f"temp_{kit_id}"
        temp_dir.mkdir(exist_ok=True)
        
        zip_file = temp_dir / "kit.zip"
        
        # Download
        if not self.download_file(kit_info['url'], zip_file):
            return False
        
        # Estrazione
        extract_dir = temp_dir / "extracted"
        if not self.extract_zip(zip_file, extract_dir):
            return False
        
        # Organizzazione
        self.organize_samples(extract_dir, kit_id)
        
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        print(f"\n✅ Kit '{kit_info['name']}' installato con successo!")
        return True
    
    def list_available_kits(self):
        """Lista tutti i kit disponibili"""
        print("\n" + "="*60)
        print("Kit di Suoni Disponibili")
        print("="*60 + "\n")
        
        for kit_id, kit_info in DRUM_KITS.items():
            print(f"ID: {kit_id}")
            print(f"  Nome: {kit_info['name']}")
            print(f"  Descrizione: {kit_info['description']}")
            print(f"  Licenza: {kit_info['license']}")
            print()
    
    def install_kit_to_library(self, kit_id: str):
        """
        Installa un kit nella libreria DrumMan
        
        Args:
            kit_id: ID del kit
        """
        kit_dir = self.kits_dir / kit_id
        
        if not kit_dir.exists():
            print(f"❌ Kit '{kit_id}' non trovato. Scaricalo prima.")
            return False
        
        metadata_file = kit_dir / "metadata.json"
        if not metadata_file.exists():
            print(f"❌ Metadata del kit '{kit_id}' non trovato")
            return False
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        print(f"\n📦 Installazione kit '{metadata['name']}' nella libreria...")
        
        # Carica libreria
        try:
            from src.sound_library import SoundLibrary
            library = SoundLibrary(str(self.sounds_dir))
            
            # Carica campioni
            samples = metadata.get('samples', {})
            loaded = 0
            
            for component, file_paths in samples.items():
                if file_paths:
                    # Usa il primo file trovato per ogni componente
                    file_path = file_paths[0]
                    if library.load_sample_from_file(component, file_path):
                        loaded += 1
                        print(f"  ✓ {component}: {Path(file_path).name}")
            
            print(f"\n✅ Installati {loaded} campioni nella libreria!")
            return True
            
        except ImportError:
            print("❌ SoundLibrary non disponibile. Installa: pip install soundfile")
            return False


def main():
    """Funzione principale"""
    print("="*60)
    print("DrumMan - Downloader Kit Suoni")
    print("="*60)
    print()
    
    downloader = DrumKitDownloader()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            downloader.list_available_kits()
        
        elif command == "download":
            if len(sys.argv) > 2:
                kit_id = sys.argv[2]
                downloader.download_kit(kit_id)
            else:
                print("❌ Specifica ID kit: python download_drum_kits.py download <kit_id>")
                downloader.list_available_kits()
        
        elif command == "install":
            if len(sys.argv) > 2:
                kit_id = sys.argv[2]
                downloader.install_kit_to_library(kit_id)
            else:
                print("❌ Specifica ID kit: python download_drum_kits.py install <kit_id>")
        
        else:
            print(f"❌ Comando sconosciuto: {command}")
    else:
        # Menu interattivo
        print("Comandi disponibili:")
        print("  list              - Lista kit disponibili")
        print("  download <id>     - Scarica un kit")
        print("  install <id>      - Installa kit nella libreria")
        print()
        print("Esempi:")
        print("  python download_drum_kits.py list")
        print("  python download_drum_kits.py download free_drum_kit_1")
        print("  python download_drum_kits.py install free_drum_kit_1")
        print()
        
        downloader.list_available_kits()


if __name__ == "__main__":
    main()

