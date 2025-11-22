# Integrazione con Reaper DAW

## Panoramica

DrumMan può essere collegato a **Reaper DAW** per inviare trigger MIDI o OSC, permettendo di usare i suoni di batteria di Reaper invece (o insieme) ai suoni sintetizzati.

## Installazione Dipendenze

### Opzione 1: Installazione Completa
```bash
pip install -r requirements.txt
```

### Opzione 2: Solo Reaper (se già hai le altre dipendenze)
```bash
pip install mido python-rtmidi python-osc
```

## Configurazione

### 1. Abilita Reaper in `src/config.py`

```python
# Configurazione Reaper
REAPER_ENABLED = True  # Abilita connessione a Reaper
REAPER_CONNECTION_TYPE = 'midi'  # 'midi', 'osc', o 'both'
REAPER_MIDI_PORT = None  # None = auto-detect
REAPER_OSC_HOST = '127.0.0.1'
REAPER_OSC_PORT = 8000
```

### 2. Configura Reaper

#### Per MIDI:

1. **Apri Reaper**
2. **Vai su Options → Preferences → Audio → MIDI Devices**
3. **Abilita un dispositivo MIDI virtuale** (es. LoopMIDI, Virtual MIDI Cable)
4. **Crea una nuova traccia**
5. **Aggiungi un VST drum machine** (es. MT Power Drum Kit, SSD5, etc.)
6. **Imposta la traccia per ricevere MIDI dal canale 10** (GM Drum Channel)

#### Per OSC:

1. **Vai su Options → Preferences → Control/OSC/web**
2. **Abilita "Enable"**
3. **Imposta porta** (default: 8000)
4. **Aggiungi un dispositivo OSC** se necessario

## Mappatura Note MIDI

DrumMan usa la **GM Drum Map** standard:

| Componente | Nota MIDI | Nome |
|------------|-----------|------|
| Kick | 36 (C2) | Kick Drum |
| Snare | 38 (D2) | Snare Drum |
| Hi-Hat | 42 (F#2) | Hi-Hat Closed |
| Crash | 49 (C#3) | Crash Cymbal |
| Tom1 | 47 (B2) | Low-Mid Tom |
| Tom2 | 48 (C3) | Hi-Mid Tom |

## Mappatura OSC

I percorsi OSC sono:

- `/drum/kick`
- `/drum/snare`
- `/drum/hihat`
- `/drum/crash`
- `/drum/tom1`
- `/drum/tom2`

Ogni messaggio OSC contiene un valore float (0-1) rappresentante la velocity.

## Utilizzo

### Avvio con Reaper

1. **Avvia Reaper** e configura una traccia drum
2. **Avvia DrumMan**:
   ```bash
   python main.py
   ```
3. **Verifica connessione**: Dovresti vedere messaggi come:
   ```
   ✅ MIDI connesso a: LoopMIDI Port
   ✅ Reaper Connector abilitato
   ```

### Modalità di Funzionamento

DrumMan può funzionare in **3 modalità**:

1. **Solo Locale**: Suoni sintetizzati (default)
2. **Solo Reaper**: Solo trigger MIDI/OSC a Reaper
3. **Entrambi**: Suoni locali + trigger a Reaper

## Troubleshooting

### MIDI non funziona

**Problema**: "Nessuna porta MIDI disponibile"

**Soluzioni**:
1. Installa un driver MIDI virtuale:
   - **Windows**: LoopMIDI, Virtual MIDI Cable
   - **macOS**: IAC Driver (built-in)
   - **Linux**: ALSA MIDI, JACK

2. Verifica porte disponibili:
   ```python
   from src.reaper_connector import ReaperConnector
   connector = ReaperConnector()
   print(connector.get_available_midi_ports())
   ```

3. Imposta porta manualmente in `config.py`:
   ```python
   REAPER_MIDI_PORT = "LoopMIDI Port"  # Nome esatto della porta
   ```

### OSC non funziona

**Problema**: "Errore inizializzazione OSC"

**Soluzioni**:
1. Verifica che Reaper abbia OSC abilitato
2. Controlla porta OSC (default: 8000)
3. Verifica firewall non blocchi la porta
4. Prova a cambiare porta in `config.py`

### Latenza

**Problema**: Latenza elevata tra movimento e suono

**Soluzioni**:
1. Usa driver audio ASIO (Windows) o CoreAudio (macOS)
2. Riduci buffer size in Reaper
3. Usa MIDI invece di OSC (generalmente più veloce)
4. Verifica che Reaper non abbia delay aggiuntivi

## Esempi di Setup Reaper

### Setup Base con VST Drum Machine

1. **Crea traccia MIDI** in Reaper
2. **Aggiungi VST** (es. MT Power Drum Kit)
3. **Imposta input MIDI** al canale 10
4. **Mappa le note** secondo GM Drum Map

### Setup Avanzato con Multiple Tracce

1. **Crea 6 tracce** (una per componente)
2. **Ogni traccia riceve una nota specifica**:
   - Tracce 1: Kick (nota 36)
   - Tracce 2: Snare (nota 38)
   - etc.
3. **Aggiungi VST diversi** per ogni traccia

### Setup OSC

1. **Installa ReaScript** per OSC in Reaper
2. **Configura percorsi OSC** per ogni componente
3. **Usa valori OSC** per modulare parametri

## API Programmabile

Puoi anche usare il ReaperConnector programmaticamente:

```python
from src.reaper_connector import ReaperConnector, ConnectionType

# Crea connettore
connector = ReaperConnector(
    connection_type=ConnectionType.MIDI,
    midi_port="LoopMIDI Port"
)

# Abilita
connector.enable()

# Invia trigger
connector.send_trigger('kick', velocity=0.8)
connector.send_trigger('snare', velocity=0.6)

# Statistiche
stats = connector.get_statistics()
print(f"MIDI messages sent: {stats['stats']['midi_messages_sent']}")

# Chiudi
connector.close()
```

## Note Importanti

- **Canale MIDI**: DrumMan usa sempre il **canale 10** (GM Drum Channel)
- **Velocity**: I valori sono normalizzati 0-1 e convertiti a 0-127 per MIDI
- **Debounce**: C'è un debounce di 10ms per evitare doppi trigger
- **Porte MIDI**: Se non specifichi una porta, DrumMan cerca automaticamente "Reaper" o usa la prima disponibile

## Supporto

Per problemi o domande:
- Controlla i log nella console
- Verifica configurazione Reaper
- Testa con un client MIDI/OSC esterno

---

**Buon divertimento con Reaper! 🎵**

