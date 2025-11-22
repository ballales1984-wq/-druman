# Kit di Suoni DrumMan

DrumMan supporta diversi kit di suoni di batteria che possono essere scaricati e utilizzati nel programma.

## Kit Disponibili

### 1. Kit Sintetizzato (Sempre Disponibile)

Il kit sintetizzato viene generato automaticamente usando la sintesi della drum machine. Include:
- **kick.wav** - Cassa
- **snare.wav** - Rullante
- **hihat.wav** - Hi-hat
- **crash.wav** - Crash cymbal
- **tom1.wav** - Tom basso
- **tom2.wav** - Tom alto

**Percorso**: `sounds/kits/synthesized/`

Questo kit è sempre disponibile e viene generato automaticamente se non presente.

### 2. Kit Online (Opzionale)

Lo script tenta di scaricare kit gratuiti da fonti online. Se il download fallisce, viene utilizzato il kit sintetizzato come fallback.

## Setup Automatico

Per scaricare e configurare tutti i kit disponibili:

```bash
python scripts/download_and_setup_kits.py
```

Questo script:
1. Genera il kit sintetizzato (se non presente)
2. Tenta di scaricare kit online
3. Carica i suoni nella libreria DrumMan

## Setup Manuale

### Aggiungere Kit Personalizzati

1. Scarica o crea file audio WAV/MP3 per ogni componente
2. Organizza i file in una cartella (es. `sounds/kits/my_kit/`)
3. Usa nomi che contengano:
   - `kick`, `bass`, `bd` per la cassa
   - `snare`, `sn`, `sd` per il rullante
   - `hihat`, `hh`, `hat` per l'hi-hat
   - `crash`, `cr` per il crash
   - `tom1`, `tom-low` per il tom basso
   - `tom2`, `tom-high` per il tom alto

4. Carica nella libreria:
   ```bash
   python -m src.sound_library_ui
   ```
   Oppure usa:
   ```python
   from src.sound_library import SoundLibrary
   library = SoundLibrary("sounds")
   library.import_samples_from_folder("sounds/kits/my_kit")
   ```

## Utilizzo nel Programma

### Modalità Sintesi (Default)

Per default, DrumMan usa la sintesi per generare i suoni. I parametri possono essere modificati nel codice.

### Modalità Libreria Suoni

Per usare i kit scaricati:

1. Modifica `src/config.py`:
   ```python
   USE_SOUND_LIBRARY = True
   SOUND_LIBRARY_PATH = "sounds"
   ```

2. Oppure passa i parametri a `DrumMachine`:
   ```python
   drum_machine = DrumMachine(
       use_sound_library=True,
       library_path="sounds"
   )
   ```

## Fonti Kit Gratuiti

Ecco alcune fonti dove puoi trovare kit di suoni gratuiti:

1. **Freesound.org** - Vasta collezione di campioni CC
2. **Loopmasters** - Kit gratuiti periodici
3. **Splice Sounds** - Campioni gratuiti
4. **GitHub** - Repository con campioni open source

**Nota**: Assicurati di rispettare le licenze dei kit scaricati.

## Formati Supportati

- WAV (consigliato)
- MP3
- FLAC
- OGG
- AIFF

## Struttura Directory

```
sounds/
├── kits/
│   ├── synthesized/          # Kit sintetizzato
│   │   ├── kick.wav
│   │   ├── snare.wav
│   │   └── ...
│   └── my_kit/              # Kit personalizzato
│       ├── kick.wav
│       └── ...
└── library.json             # Metadata libreria
```

## Troubleshooting

### Kit non caricati

Se i kit non vengono caricati:
1. Verifica che i file siano in formato supportato
2. Controlla i nomi dei file (devono contenere le parole chiave)
3. Verifica i permessi di lettura della directory

### Suoni non riprodotti

Se i suoni non vengono riprodotti:
1. Verifica che `USE_SOUND_LIBRARY = True` in config
2. Controlla che la libreria sia stata inizializzata correttamente
3. Verifica i log per errori di caricamento

## Personalizzazione

Puoi modificare i suoni usando l'interfaccia grafica:

```bash
python -m src.sound_library_ui
```

Oppure programmaticamente:

```python
from src.sound_library import SoundLibrary

library = SoundLibrary("sounds")
sample = library.get_sample("kick")

# Modifica parametri
sample.set_parameter("volume", 0.8)
sample.set_parameter("pitch", 1.1)
sample.set_parameter("reverb", 0.3)

# Applica modifiche
sample.apply_modifications()
```

