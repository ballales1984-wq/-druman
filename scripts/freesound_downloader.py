"""
Downloader per campioni da Freesound.org
Richiede API key (gratuita)
"""
import os
import sys
import urllib.request
import json
from pathlib import Path

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

# Istruzioni per ottenere API key:
# 1. Vai su https://freesound.org/apiv2/apply/
# 2. Registrati e richiedi API key
# 3. Inserisci la key qui o in .env

FREESOUND_API_KEY = os.getenv("FREESOUND_API_KEY", "")
FREESOUND_API_URL = "https://freesound.org/apiv2"


class FreesoundDownloader:
    """Downloader per Freesound.org"""
    
    def __init__(self, api_key: str = None):
        """
        Inizializza downloader
        
        Args:
            api_key: API key Freesound (opzionale, può essere in .env)
        """
        self.api_key = api_key or FREESOUND_API_KEY
        self.sounds_dir = Path("sounds/kits/freesound")
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
    
    def search_samples(self, query: str, limit: int = 10):
        """
        Cerca campioni su Freesound
        
        Args:
            query: Query di ricerca
            limit: Numero massimo risultati
        """
        if not self.api_key:
            print("❌ API key Freesound non configurata!")
            print("   Ottieni una key gratuita su: https://freesound.org/apiv2/apply/")
            return []
        
        try:
            url = f"{FREESOUND_API_URL}/search/text/?query={query}&fields=id,name,previews&token={self.api_key}"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                return data.get('results', [])[:limit]
        except Exception as e:
            print(f"❌ Errore ricerca: {e}")
            return []
    
    def download_sample(self, sound_id: int, component_name: str):
        """
        Scarica un campione
        
        Args:
            sound_id: ID del suono su Freesound
            component_name: Nome componente (kick, snare, etc.)
        """
        if not self.api_key:
            print("❌ API key non configurata!")
            return False
        
        try:
            # Ottieni info suono
            info_url = f"{FREESOUND_API_URL}/sounds/{sound_id}/?token={self.api_key}"
            with urllib.request.urlopen(info_url) as response:
                sound_info = json.loads(response.read())
            
            # Download preview (MP3)
            preview_url = sound_info.get('previews', {}).get('preview-hq-mp3')
            if not preview_url:
                print(f"❌ Preview non disponibile per sound {sound_id}")
                return False
            
            # Scarica
            file_path = self.sounds_dir / f"{component_name}_{sound_id}.mp3"
            urllib.request.urlretrieve(preview_url, file_path)
            
            print(f"✅ Scaricato: {sound_info['name']} → {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Errore download: {e}")
            return False


def download_basic_drum_kit():
    """Scarica un kit base da Freesound (richiede API key)"""
    print("="*60)
    print("Freesound Drum Kit Downloader")
    print("="*60)
    print()
    
    downloader = FreesoundDownloader()
    
    if not downloader.api_key:
        print("⚠️  API key non configurata!")
        print("\nPer usare Freesound:")
        print("1. Vai su https://freesound.org/apiv2/apply/")
        print("2. Registrati e ottieni API key gratuita")
        print("3. Imposta variabile d'ambiente:")
        print("   export FREESOUND_API_KEY='tua_key'")
        print("   oppure aggiungi in .env file")
        return
    
    # Ricerche per ogni componente
    searches = {
        'kick': 'drum kick bass',
        'snare': 'drum snare',
        'hihat': 'drum hihat hi-hat',
        'crash': 'drum crash cymbal',
        'tom1': 'drum tom low',
        'tom2': 'drum tom high'
    }
    
    print("Ricerca campioni...")
    for component, query in searches.items():
        print(f"\n{component.upper()}:")
        results = downloader.search_samples(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['name']} (ID: {result['id']})")
            
            # Scarica il primo risultato
            if results:
                downloader.download_sample(results[0]['id'], component)
        else:
            print("  Nessun risultato trovato")
    
    print("\n✅ Download completato!")


if __name__ == "__main__":
    download_basic_drum_kit()

