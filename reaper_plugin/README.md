# DrumMan Reaper Plugin

Interfaccia plugin per integrare DrumMan con Reaper DAW.

## Componenti

### 1. DrumMan_Reaper_Plugin.py
ReaScript Python per Reaper. Si integra direttamente nell'interfaccia di Reaper.

**Installazione:**
```bash
python install_plugin.py
```

Oppure manualmente:
1. Copia `DrumMan_Reaper_Plugin.py` in `Reaper/Scripts/`
2. In Reaper: Actions → Show action list → Load ReaScript
3. Seleziona il file
4. Assegna una shortcut

### 2. DrumMan_Standalone_GUI.py
Interfaccia grafica standalone che funziona come plugin esterno.

**Uso:**
```bash
python reaper_plugin/DrumMan_Standalone_GUI.py
```

## Funzionalità

- ✅ Connessione MIDI/OSC a Reaper
- ✅ Monitoraggio trigger in tempo reale
- ✅ Statistiche dettagliate
- ✅ Configurazione porte MIDI
- ✅ Interfaccia grafica intuitiva

## Requisiti

- Reaper DAW installato
- Python 3.8+
- Dipendenze: `mido`, `python-rtmidi`, `python-osc`
- Driver MIDI virtuale (LoopMIDI, IAC Driver, etc.)

## Configurazione Reaper

1. **Apri Reaper**
2. **Crea traccia MIDI**
3. **Imposta Input MIDI** su canale 10
4. **Aggiungi VST drum machine**
5. **Avvia DrumMan e il plugin**

## Troubleshooting

### Plugin non appare in Reaper
- Verifica che il file sia in `Reaper/Scripts/`
- Controlla che Reaper supporti Python ReaScript
- Riavvia Reaper

### Nessuna connessione
- Verifica che DrumMan sia in esecuzione
- Controlla porte MIDI disponibili
- Verifica configurazione in Reaper

## Documentazione

Vedi `docs/REAPER_INTEGRATION.md` per la guida completa.

