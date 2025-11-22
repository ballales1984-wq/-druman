# Libreria Suoni Modificabile

## Panoramica

DrumMan include un sistema completo di **libreria suoni modificabile** che permette di:
- Caricare suoni campionati (WAV, MP3, FLAC, etc.)
- Modificare parametri audio in tempo reale
- Salvare e caricare preset
- Esportare suoni modificati

## Caratteristiche

### Parametri Modificabili

- **Volume**: 0.0 - 2.0
- **Pitch**: 0.5 - 2.0 (shift tonale)
- **Velocità**: 0.5 - 2.0 (velocità riproduzione)
- **Envelope ADSR**:
  - Attack: 0.0 - 1.0
  - Decay: 0.0 - 1.0
  - Sustain: 0.0 - 1.0
  - Release: 0.0 - 1.0
- **Filtri**:
  - Lowpass: 20 - 20000 Hz
  - Highpass: 0 - 20000 Hz
- **Effetti**:
  - Riverbero: 0.0 - 1.0
  - Distorsione: 0.0 - 1.0
- **Panoramica**: -1.0 (sinistra) a 1.0 (destra)

## Utilizzo

### Avvia Gestore Libreria

```bash
python sound_library_manager.py
```

Oppure:
```bash
python src/sound_library_ui.py
```

### Interfaccia

L'interfaccia è divisa in 3 sezioni:

1. **Sinistra - Campioni**:
   - Lista campioni caricati
   - Pulsanti: Carica File, Carica Cartella, Rimuovi, Esporta

2. **Centro - Parametri**:
   - Slider per ogni parametro
   - Valore corrente visualizzato
   - Pulsante Reset per ogni parametro
   - Reset Tutti i Parametri

3. **Destra - Preset**:
   - Lista preset salvati
   - Salva/Carica/Elimina preset
   - Campo nome preset

### Caricare Suoni

#### Metodo 1: Singolo File
1. Clicca "Carica File"
2. Seleziona file audio (WAV, MP3, FLAC, etc.)
3. Inserisci nome componente (kick, snare, etc.)
4. Il suono viene caricato e applicato automaticamente

#### Metodo 2: Cartella Intera
1. Clicca "Carica Cartella"
2. Seleziona cartella con file audio
3. I file vengono caricati automaticamente
4. Il nome componente viene dedotto dal nome file

### Modificare Suoni

1. **Seleziona un campione** dalla lista
2. **Regola i parametri** con gli slider
3. **Vedi il valore** aggiornato in tempo reale
4. **Reset singolo parametro** o tutti insieme
5. Le modifiche sono applicate immediatamente

### Preset

#### Salvare Preset
1. Modifica i parametri dei campioni
2. Inserisci nome preset
3. Clicca "Salva Preset"
4. Il preset salva tutti i parametri di tutti i campioni

#### Caricare Preset
1. Seleziona preset dalla lista
2. Clicca "Carica Preset"
3. Tutti i parametri vengono ripristinati

#### Eliminare Preset
1. Seleziona preset
2. Clicca "Elimina Preset"

### Esportare Suoni

1. Seleziona campione da esportare
2. Clicca "Esporta"
3. Scegli percorso e nome file
4. Il suono modificato viene salvato come WAV

## Integrazione con Drum Machine

### Abilitare Libreria

Modifica `src/config.py` o nel codice:

```python
from src.drum_machine import DrumMachine
from src.sound_library import SoundLibrary

# Crea drum machine con libreria
drum_machine = DrumMachine(
    use_sound_library=True,
    library_path="sounds"
)
```

### Usare Libreria nel Main

Il `main.py` può essere modificato per usare la libreria:

```python
drum_machine = DrumMachine(
    use_sound_library=True,  # Abilita libreria
    library_path="sounds"     # Percorso libreria
)
```

## Struttura File

```
sounds/
├── library.json          # Database libreria (parametri, preset)
├── kick.wav              # File audio (opzionale, se salvati qui)
├── snare.wav
└── ...
```

## Formati Supportati

- **WAV** (consigliato)
- **MP3**
- **FLAC**
- **OGG**
- **AIFF**

## Esempi di Utilizzo Programmabile

### Caricare Campione

```python
from src.sound_library import SoundLibrary, SoundSample

library = SoundLibrary("sounds")

# Carica da file
library.load_sample_from_file("kick", "path/to/kick.wav")

# Crea campione da array numpy
audio_data = np.array([...])  # Dati audio
sample = SoundSample("kick", audio_data=audio_data)
library.add_sample("kick", sample)
```

### Modificare Parametri

```python
sample = library.get_sample("kick")

# Modifica parametri
sample.set_parameter("volume", 1.5)
sample.set_parameter("pitch", 0.8)
sample.set_parameter("reverb", 0.3)

# Applica modifiche
audio = sample.apply_modifications()
```

### Preset

```python
# Salva preset
library.save_preset("rock_preset")

# Carica preset
library.load_preset("rock_preset")

# Lista preset
presets = library.list_presets()
```

## Suggerimenti

1. **Usa WAV** per migliore qualità e compatibilità
2. **Sample Rate**: 44100 Hz è consigliato
3. **Mono o Stereo**: Entrambi supportati
4. **Durata**: Suoni brevi (0.1-2s) funzionano meglio
5. **Normalizzazione**: I file vengono normalizzati automaticamente

## Troubleshooting

### File non si carica
- Verifica formato supportato
- Controlla che il file non sia corrotto
- Verifica permessi file

### Modifiche non si applicano
- Seleziona il campione dalla lista
- Verifica che i parametri siano cambiati
- Prova a resettare e riapplicare

### Libreria non si salva
- Verifica permessi directory
- Controlla spazio disco
- Verifica che la directory esista

---

**Crea la tua libreria personalizzata! 🎵**

