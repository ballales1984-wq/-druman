# Quick Start - Kit Suoni

## Setup Rapido

Per scaricare e configurare i kit di suoni:

```bash
python scripts/download_and_setup_kits.py
```

Questo comando:
- ✅ Genera automaticamente un kit sintetizzato (sempre disponibile)
- ✅ Tenta di scaricare kit online (opzionale)
- ✅ Carica i suoni nella libreria DrumMan

## Utilizzo

### Opzione 1: Kit Sintetizzato (Default)

Il kit sintetizzato è già configurato e pronto all'uso. Basta avviare DrumMan:

```bash
python main.py
```

### Opzione 2: Kit Personalizzati

1. Metti i tuoi file WAV/MP3 in `sounds/kits/my_kit/`
2. Usa nomi che contengano: `kick`, `snare`, `hihat`, `crash`, `tom1`, `tom2`
3. Carica nella libreria:
   ```bash
   python -m src.sound_library_ui
   ```
   Oppure usa lo script:
   ```bash
   python scripts/download_and_setup_kits.py
   ```

## Configurazione

Per usare i kit scaricati invece della sintesi, verifica che in `src/config.py`:

```python
USE_SOUND_LIBRARY = True
SOUND_LIBRARY_PATH = "sounds"
```

## Verifica

Dopo lo setup, verifica che i kit siano stati caricati:

```bash
# Controlla i file
ls sounds/kits/synthesized/

# Dovresti vedere:
# kick.wav, snare.wav, hihat.wav, crash.wav, tom1.wav, tom2.wav
```

## Troubleshooting

**Problema**: I suoni non vengono riprodotti
- Verifica che `USE_SOUND_LIBRARY = True` in `src/config.py`
- Controlla che i file siano in `sounds/kits/synthesized/`

**Problema**: Download kit online fallito
- Non è un problema! Il kit sintetizzato è sempre disponibile
- Puoi aggiungere kit manualmente copiando file in `sounds/kits/`

## Fonti Kit Gratuiti

- **Freesound.org** - Campioni CC
- **Loopmasters** - Kit gratuiti
- **Splice Sounds** - Campioni gratuiti

Per maggiori dettagli, vedi `docs/DRUM_KITS.md`

