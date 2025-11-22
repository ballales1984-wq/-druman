# 🚀 Quick Start - Collegare DrumMan a Reaper

## Setup Rapido (5 minuti)

### 1. Installa Dipendenze

```bash
pip install mido python-rtmidi python-osc
```

### 2. Installa Driver MIDI Virtuale

**Windows:**
- Scarica e installa [LoopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
- Crea una nuova porta MIDI chiamata "DrumMan"

**macOS:**
- Vai su Audio MIDI Setup → IAC Driver
- Abilita "IAC Driver"

**Linux:**
- Usa ALSA o JACK (già incluso nella maggior parte delle distribuzioni)

### 3. Configura Reaper

1. **Apri Reaper**
2. **Crea una nuova traccia MIDI**
3. **Vai su Options → Preferences → Audio → MIDI Devices**
4. **Abilita la porta MIDI virtuale** (LoopMIDI o IAC Driver)
5. **Nella traccia, imposta Input MIDI** al canale 10
6. **Aggiungi un VST drum machine** (es. MT Power Drum Kit - gratuito)

### 4. Abilita Reaper in DrumMan

Modifica `src/config.py`:

```python
REAPER_ENABLED = True
REAPER_CONNECTION_TYPE = 'midi'  # o 'osc' o 'both'
REAPER_MIDI_PORT = None  # None = auto-detect
```

### 5. Avvia

```bash
python main.py
```

Dovresti vedere:
```
✅ MIDI connesso a: LoopMIDI Port
✅ Reaper Connector abilitato
```

### 6. Suona!

Muoviti davanti alla camera e i trigger verranno inviati a Reaper!

## Mappatura Note

| Movimento | Nota MIDI | Componente |
|-----------|----------|------------|
| Piede | 36 | Kick |
| Mano sinistra | 38 | Snare |
| Mano destra | 42 | Hi-Hat |
| Mano alta destra | 49 | Crash |
| Mano sinistra centro | 47 | Tom1 |
| Mano destra centro | 48 | Tom2 |

## Troubleshooting

**"Nessuna porta MIDI disponibile"**
→ Installa LoopMIDI (Windows) o abilita IAC Driver (macOS)

**"Reaper non riceve MIDI"**
→ Verifica che la traccia sia impostata su canale 10 (GM Drum Channel)

**Latenza elevata**
→ Usa driver ASIO (Windows) o CoreAudio (macOS), riduci buffer in Reaper

## Documentazione Completa

Vedi `docs/REAPER_INTEGRATION.md` per la guida completa.

---

**Pronto! Buon divertimento! 🥁🎵**

