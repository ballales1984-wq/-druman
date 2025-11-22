# 🎵 Quick Start - Libreria Suoni

## Setup Rapido

### 1. Installa Dipendenza

```bash
pip install soundfile
```

### 2. Avvia Gestore Libreria

```bash
python sound_library_manager.py
```

## Utilizzo Base

### Caricare Suoni

1. **Clicca "Carica File"**
2. **Seleziona file audio** (WAV, MP3, FLAC, etc.)
3. **Inserisci nome componente** (kick, snare, hihat, etc.)
4. **Il suono viene caricato!**

### Modificare Suoni

1. **Seleziona campione** dalla lista
2. **Regola slider** per modificare parametri:
   - Volume, Pitch, Velocità
   - Attack, Decay, Sustain, Release
   - Filtri (Lowpass, Highpass)
   - Effetti (Riverbero, Distorsione)
   - Panoramica
3. **Vedi modifiche in tempo reale**

### Salvare Preset

1. **Modifica parametri** dei campioni
2. **Inserisci nome preset**
3. **Clicca "Salva Preset"**
4. **Il preset salva tutti i parametri**

### Usare Libreria in DrumMan

Modifica `src/config.py`:

```python
USE_SOUND_LIBRARY = True
SOUND_LIBRARY_PATH = "sounds"
```

Poi avvia normalmente:
```bash
python main.py
```

## Formati Supportati

- ✅ WAV (consigliato)
- ✅ MP3
- ✅ FLAC
- ✅ OGG
- ✅ AIFF

## Suggerimenti

- **Usa WAV** per migliore qualità
- **Sample rate 44100 Hz** consigliato
- **Suoni brevi** (0.1-2s) funzionano meglio
- **Salva preset** per configurazioni diverse

---

**Crea la tua libreria personalizzata! 🎵**

