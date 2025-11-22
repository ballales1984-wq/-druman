# 🥁 Guida all'Uso - DrumMan

Guida pratica passo-passo per usare DrumMan.

## 📋 Indice Rapido

1. [Installazione](#installazione)
2. [Primo Avvio](#primo-avvio)
3. [Come Suonare](#come-suonare)
4. [Controlli](#controlli)
5. [Configurazione](#configurazione)
6. [Kit di Suoni](#kit-di-suoni)
7. [Integrazione Reaper](#integrazione-reaper)
8. [Risoluzione Problemi](#risoluzione-problemi)

---

## 🚀 Installazione

### Passo 1: Verifica Python

Apri il terminale e verifica che Python sia installato:

```bash
python --version
```

Deve essere **Python 3.8 o superiore**.

### Passo 2: Installa Dipendenze

**Windows:**
```bash
setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Oppure manualmente:**
```bash
pip install -r requirements.txt
```

### Passo 3: Setup Kit Suoni (Opzionale)

Per avere suoni pronti all'uso:

```bash
python scripts/download_and_setup_kits.py
```

Questo genera automaticamente un kit sintetizzato.

---

## 🎬 Primo Avvio

### Avvia l'Applicazione

```bash
python main.py
```

### Prima Volta - Setup Camera

1. **Posizionati davanti alla webcam**
   - Distanza: 1-2 metri
   - Assicurati di essere ben visibile
   - Buona illuminazione

2. **Esegui la Calibrazione**
   - Premi `TAB` per aprire il menu
   - Premi `C` per entrare nel menu Calibrazione
   - Premi `SPACE` per avviare (5 secondi)
   - Muoviti naturalmente durante la calibrazione

3. **Pronto!** Ora puoi suonare

---

## 🎮 Come Suonare

### Posizione Base

- **Mani**: Muovi le mani come se stessi suonando una batteria
- **Piedi**: Muovi i piedi per la cassa (kick)
- **Corpo**: Stai in piedi, ben visibile dalla camera

### Zone della Batteria

| Componente | Posizione | Come Attivarlo |
|------------|-----------|----------------|
| **Kick** (Cassa) | Basso centrale | Muovi i piedi verso il basso |
| **Snare** (Rullante) | Centro | Colpisci con le mani al centro |
| **Hi-Hat** | Sinistra alta | Mano sinistra in alto |
| **Crash** | Destra alta | Mano destra in alto |
| **Tom1** | Sinistra centro | Mano sinistra a sinistra |
| **Tom2** | Destra centro | Mano destra a destra |

### Suggerimenti

- **Movimenti ampi**: Fai movimenti chiari e ampi
- **Velocità**: Più veloce il movimento, più forte il suono
- **Distanza**: Avvicinati alle zone per attivarle
- **Pratica**: Inizia lentamente, poi aumenta la velocità

---

## ⌨️ Controlli

### Controlli Principali

| Tasto | Azione |
|-------|--------|
| `TAB` | Apri/Chiudi Menu |
| `ESC` | Esci dall'applicazione |

### Menu Metronomo (M)

Nel menu, premi `M` per entrare nel menu Metronomo:

| Tasto | Azione |
|-------|--------|
| `SPACE` | Attiva/Disattiva Metronomo |
| `↑` | Aumenta BPM (+5) |
| `↓` | Diminuisci BPM (-5) |
| `M` | Torna al menu principale |

### Menu Volume (V)

Nel menu, premi `V` per entrare nel menu Volume:

| Tasto | Azione |
|-------|--------|
| `↑` | Aumenta Volume (+10%) |
| `↓` | Diminuisci Volume (-10%) |
| `V` | Torna al menu principale |

### Menu Calibrazione (C)

Nel menu, premi `C` per entrare nel menu Calibrazione:

| Tasto | Azione |
|-------|--------|
| `SPACE` | Avvia Calibrazione (5 secondi) |
| `C` | Torna al menu principale |

**Nota**: Esegui la calibrazione se il tracking non è preciso.

---

## ⚙️ Configurazione

### File di Configurazione

Modifica `src/config.py` per personalizzare:

#### Camera

```python
CAMERA_INDEX = 0  # Cambia se hai più camere (0, 1, 2...)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
```

#### Audio

```python
USE_SOUND_LIBRARY = True  # Usa kit scaricati invece di sintesi
SOUND_LIBRARY_PATH = "sounds"  # Percorso libreria suoni
```

#### Sensibilità

```python
VELOCITY_THRESHOLD = 0.3  # Velocità minima per trigger (0-1)
COOLDOWN_TIME = 0.1  # Secondi tra colpi (evita doppi trigger)
```

#### Zone Batteria

Puoi modificare posizione e dimensione delle zone:

```python
DRUM_ZONES = {
    'kick': {
        'center': np.array([0.5, 0.7, 0.0]),  # x, y, z (0-1)
        'radius': 0.15,  # Dimensione zona
        'trigger_distance': 0.2  # Distanza per attivare
    },
    # ... altre zone
}
```

---

## 🎵 Kit di Suoni

### Usare Kit Scaricati

I kit sono già configurati. Per verificare:

```bash
# Controlla i file
dir sounds\kits\synthesized
```

Dovresti vedere: `kick.wav`, `snare.wav`, `hihat.wav`, `crash.wav`, `tom1.wav`, `tom2.wav`

### Aggiungere Kit Personalizzati

1. **Prepara i file audio** (WAV/MP3)
2. **Crea una cartella**: `sounds/kits/mio_kit/`
3. **Usa nomi che contengano**:
   - `kick`, `bass`, `bd` per la cassa
   - `snare`, `sn`, `sd` per il rullante
   - `hihat`, `hh`, `hat` per l'hi-hat
   - `crash`, `cr` per il crash
   - `tom1`, `tom-low` per il tom basso
   - `tom2`, `tom-high` per il tom alto

4. **Carica nella libreria**:
   ```bash
   python -m src.sound_library_ui
   ```
   Oppure:
   ```bash
   python scripts/download_and_setup_kits.py
   ```

### Modificare Suoni

Per modificare volume, pitch, effetti:

```bash
python -m src.sound_library_ui
```

Interfaccia grafica per:
- Caricare file audio
- Modificare parametri (volume, pitch, reverb, etc.)
- Salvare preset
- Esportare suoni modificati

---

## 🎛️ Integrazione Reaper

### Configurazione Base

1. **Abilita Reaper** in `src/config.py`:

```python
REAPER_ENABLED = True
REAPER_CONNECTION_TYPE = 'midi'  # o 'osc', 'both'
REAPER_MIDI_PORT = None  # None = auto-detect
```

2. **Avvia Reaper** prima di DrumMan

3. **Configura Reaper**:
   - Vai in Preferences → MIDI Devices
   - Abilita "Enable input" per la porta MIDI
   - Crea una traccia MIDI e assegna un drum kit

4. **Avvia DrumMan**:
   ```bash
   python main.py
   ```

### Plugin Standalone

Per monitorare la connessione:

**Windows:**
```bash
reaper_plugin\run_standalone.bat
```

**Linux/macOS:**
```bash
chmod +x reaper_plugin/run_standalone.sh
./reaper_plugin/run_standalone.sh
```

Vedi `PLUGIN_GUIDE.md` per dettagli completi.

---

## 🔧 Risoluzione Problemi

### Camera non rilevata

**Errore**: "ERRORE: Impossibile aprire la videocamera"

**Soluzioni**:
1. Verifica che la camera sia collegata
2. Chiudi altre app che usano la camera (Zoom, Teams, etc.)
3. Cambia `CAMERA_INDEX` in `src/config.py` (prova 1, 2, 3...)
4. Su Linux: verifica permessi `/dev/video0`

### Nessun suono

**Problema**: I movimenti vengono rilevati ma non c'è audio

**Soluzioni**:
1. Verifica volume sistema operativo
2. Controlla che `USE_SOUND_LIBRARY = True` in config
3. Verifica che i file siano in `sounds/kits/synthesized/`
4. Riavvia l'applicazione

### Tracking impreciso

**Problema**: I colpi non vengono rilevati correttamente

**Soluzioni**:
1. **Migliora illuminazione**: Luce frontale, evita controluce
2. **Esegui calibrazione**: Menu → C → SPACE
3. **Aumenta sensibilità**: Riduci `VELOCITY_THRESHOLD` in config
4. **Aumenta distanza trigger**: Aumenta `trigger_distance` in config
5. **Posizionamento**: Stai a 1-2 metri dalla camera, ben visibile

### Performance basse (lag)

**Problema**: FPS bassi, ritardo nei suoni

**Soluzioni**:
1. Riduci risoluzione camera in `src/config.py`:
   ```python
   CAMERA_WIDTH = 320
   CAMERA_HEIGHT = 240
   ```
2. Chiudi altre applicazioni pesanti
3. Disabilita animazioni complesse (modifica codice se necessario)

### Errori di import

**Errore**: "ModuleNotFoundError"

**Soluzioni**:
1. Verifica ambiente virtuale attivo:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```
2. Reinstalla dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
3. Verifica Python 3.8+:
   ```bash
   python --version
   ```

### Kit suoni non caricati

**Problema**: I suoni non vengono riprodotti anche se i file esistono

**Soluzioni**:
1. Verifica formato file (WAV consigliato)
2. Esegui setup kit:
   ```bash
   python scripts/download_and_setup_kits.py
   ```
3. Verifica `USE_SOUND_LIBRARY = True` in config
4. Controlla i log all'avvio per errori

---

## 📚 Altre Funzionalità

### Simulatore Trigger

Per testare il sistema di trigger senza camera:

```bash
python simulator_app.py
```

### Test Componenti

Per verificare che tutto funzioni:

```bash
python test_components.py
```

### Esempi Trigger System

Per vedere esempi di utilizzo:

```bash
python examples/trigger_examples.py
```

---

## 💡 Suggerimenti Avanzati

### Migliorare Precisione

1. **Illuminazione uniforme**: Evita ombre forti
2. **Sfondo semplice**: Sfondo uniforme migliora il tracking
3. **Vestiti contrastanti**: Evita colori simili allo sfondo
4. **Calibrazione regolare**: Ricalibra se cambi posizione

### Performance Live

1. **Chiudi app inutili**: Libera risorse CPU/RAM
2. **Riduci risoluzione**: 320x240 è sufficiente per il tracking
3. **Disabilita effetti**: Se usi sintesi, disabilita effetti complessi
4. **Usa kit pre-generati**: Più veloce della sintesi real-time

### Personalizzazione

- **Modifica zone**: Cambia posizione e dimensione in `src/config.py`
- **Aggiungi suoni**: Aggiungi nuovi componenti modificando `drum_machine.py`
- **Personalizza colori**: Modifica `COLORS` in `src/config.py`
- **Crea preset**: Usa `sound_library_ui.py` per salvare preset personalizzati

---

## 📞 Supporto

### Documentazione Completa

- `README.md` - Documentazione completa
- `docs/DRUM_KITS.md` - Guida kit suoni
- `docs/REAPER_INTEGRATION.md` - Integrazione Reaper
- `PLUGIN_GUIDE.md` - Guida plugin Reaper

### Contatti

- **Email**: ballales1984@gmail.com
- **GitHub**: [Repository](https://github.com/ballales1984-wq/-druman.git)

---

## 🎉 Divertiti!

DrumMan è pronto all'uso. Inizia a suonare e divertiti! 🥁🎵

Per domande o problemi, consulta la documentazione o apri un issue su GitHub.

