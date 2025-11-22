# 🎛️ Guida Plugin DrumMan per Reaper

## Panoramica

DrumMan include **due tipi di interfaccia plugin** per Reaper:

1. **ReaScript Python** - Integrato direttamente in Reaper
2. **Standalone GUI** - Interfaccia grafica esterna

## 🚀 Quick Start

### Opzione 1: Standalone GUI (Consigliato per iniziare)

```bash
# Windows
reaper_plugin\run_standalone.bat

# Linux/macOS
chmod +x reaper_plugin/run_standalone.sh
./reaper_plugin/run_standalone.sh
```

Oppure:
```bash
python reaper_plugin/DrumMan_Standalone_GUI.py
```

### Opzione 2: ReaScript Python (Integrato in Reaper)

1. **Installa il plugin:**
   ```bash
   python reaper_plugin/install_plugin.py
   ```

2. **In Reaper:**
   - Actions → Show action list
   - Load ReaScript → Seleziona `DrumMan_Reaper_Plugin.py`
   - Assegna shortcut (es. Ctrl+Alt+D)

## 📋 Funzionalità Interfaccia

### Standalone GUI

- ✅ **Connessione MIDI/OSC**: Configura e connetti a Reaper
- ✅ **Monitoraggio Real-time**: Vedi i trigger in tempo reale
- ✅ **Statistiche**: Contatori per ogni componente
- ✅ **Gestione Porte**: Aggiorna e seleziona porte MIDI
- ✅ **Status Visuale**: Indicatore connessione/disconnessione

### ReaScript Plugin

- ✅ **Integrazione Nativa**: Funziona dentro Reaper
- ✅ **Statistiche**: Contatori trigger
- ✅ **Accesso Rapido**: Via shortcut personalizzata

## 🎯 Setup Completo

### 1. Prepara Reaper

1. **Apri Reaper**
2. **Crea nuova traccia MIDI**
3. **Imposta Input MIDI**:
   - Vai su traccia → Input → MIDI
   - Seleziona porta MIDI virtuale (LoopMIDI, IAC, etc.)
   - Imposta canale 10 (GM Drum Channel)
4. **Aggiungi VST Drum Machine**:
   - Clicca "FX" sulla traccia
   - Aggiungi VST (es. MT Power Drum Kit, SSD5, etc.)
   - Configura mappatura note secondo GM Drum Map

### 2. Configura DrumMan

Modifica `src/config.py`:

```python
REAPER_ENABLED = True
REAPER_CONNECTION_TYPE = 'midi'  # o 'osc' o 'both'
REAPER_MIDI_PORT = None  # None = auto-detect
```

### 3. Avvia DrumMan

```bash
python main.py
```

### 4. Avvia Plugin Interface

**Standalone:**
```bash
python reaper_plugin/DrumMan_Standalone_GUI.py
```

**ReaScript:**
- Usa la shortcut assegnata in Reaper

## 🎨 Interfaccia Standalone - Dettagli

### Sezione Connessione

- **Tipo**: Scegli MIDI, OSC o Both
- **MIDI Port**: Seleziona porta (usa "Aggiorna Porte MIDI")
- **OSC Host/Port**: Configurazione OSC
- **Pulsanti**: Connetti/Disconnetti/Refresh

### Sezione Statistiche

Mostra in tempo reale:
- **Kick**: Numero di trigger kick
- **Snare**: Numero di trigger snare
- **Hi-Hat**: Numero di trigger hi-hat
- **Crash**: Numero di trigger crash
- **Tom1/Tom2**: Numero di trigger tom
- **TOTALE**: Somma di tutti i trigger

### Pulsante Reset

Resetta tutti i contatori a zero.

## 🔧 Troubleshooting

### Standalone GUI non si connette

1. Verifica che DrumMan sia in esecuzione
2. Controlla che `REAPER_ENABLED = True` in config.py
3. Verifica porte MIDI disponibili
4. Controlla che Reaper sia configurato correttamente

### ReaScript non appare

1. Verifica installazione in `Reaper/Scripts/`
2. Controlla che Reaper supporti Python ReaScript
3. Riavvia Reaper
4. Verifica percorso file

### Trigger non arrivano a Reaper

1. Verifica connessione in Standalone GUI
2. Controlla canale MIDI (deve essere 10)
3. Verifica che traccia sia in ascolto
4. Controlla VST drum machine configurato

## 📊 Mappatura Note

| Componente | Nota MIDI | Percorso OSC |
|------------|-----------|--------------|
| Kick | 36 (C2) | `/drum/kick` |
| Snare | 38 (D2) | `/drum/snare` |
| Hi-Hat | 42 (F#2) | `/drum/hihat` |
| Crash | 49 (C#3) | `/drum/crash` |
| Tom1 | 47 (B2) | `/drum/tom1` |
| Tom2 | 48 (C3) | `/drum/tom2` |

## 💡 Suggerimenti

1. **Usa Standalone GUI** per monitoraggio e debug
2. **Usa ReaScript** per integrazione nativa in Reaper
3. **Combina entrambi** per controllo completo
4. **Monitora statistiche** per ottimizzare performance

## 📝 Note

- L'interfaccia standalone funziona indipendentemente da Reaper
- Il ReaScript richiede Reaper in esecuzione
- Entrambi possono essere usati contemporaneamente
- Le statistiche sono separate per ogni istanza

---

**Buon divertimento con il plugin! 🎵**

