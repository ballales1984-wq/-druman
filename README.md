# 🥁 DrumMan - Virtual Drum Machine con Motion Tracking

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-success.svg)]()
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/tuonome/druman)

> Un'applicazione avanzata che trasforma i tuoi movimenti in suoni di batteria virtuale usando computer vision e sintesi audio in tempo reale.

## 📋 Indice

- [Descrizione](#-descrizione)
- [Caratteristiche](#-caratteristiche)
- [Demo](#-demo)
- [Installazione](#-installazione)
- [Utilizzo](#-utilizzo)
- [Architettura](#-architettura)
- [Configurazione](#-configurazione)
- [Sviluppo](#-sviluppo)
- [Tecnologie](#-tecnologie)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [Contribuire](#-contribuire)
- [Licenza](#-licenza)

## 🎯 Descrizione

**DrumMan** è un sistema innovativo di batteria virtuale che utilizza computer vision per interpretare i movimenti del corpo e generare suoni di batteria in tempo reale. L'applicazione combina:

- **Motion Tracking Avanzato**: Rilevamento preciso delle articolazioni tramite MediaPipe Pose
- **Sintesi Audio Realistica**: Generazione di suoni di batteria con armoniche multiple e effetti
- **Visualizzazione 3D Interattiva**: Ambiente virtuale con feedback visivo in tempo reale
- **Sistema di Calibrazione**: Ottimizzazione automatica per migliori risultati

L'app è progettata per funzionare **esclusivamente con una webcam**, senza bisogno di sensori aggiuntivi o hardware specializzato, rendendola accessibile a chiunque.

## ✨ Caratteristiche

### 🎥 Motion Tracking
- ✅ Rilevamento in tempo reale di mani, piedi e corpo
- ✅ Smoothing delle posizioni per tracking fluido
- ✅ Calcolo della velocità per intensità dinamica dei colpi
- ✅ Supporto per calibrazione personalizzata

### 🥁 Drum Machine
- ✅ **6 Componenti**: Kick, Snare, Hi-Hat, Crash, Tom1, Tom2
- ✅ **Suoni Sintetizzati**: Armoniche multiple, envelope dinamici, filtri audio
- ✅ **Volume Dinamico**: Intensità basata sulla velocità del movimento
- ✅ **Metronomo Integrato**: BPM configurabile (60-200)
- ✅ **Registrazione Pattern**: Sistema per registrare e riprodurre sequenze

### 🎮 Interfaccia
- ✅ **Visualizzazione 3D**: Ambiente virtuale con proiezione ortografica
- ✅ **Animazioni**: Feedback visivo per zone attive e colpi
- ✅ **Menu Interattivo**: Configurazione in-game senza uscire
- ✅ **Informazioni Real-time**: FPS, zone attive, stato sistema

### ⚙️ Sistema Avanzato
- ✅ **Calibrazione Automatica**: Ottimizzazione del tracking in 5 secondi
- ✅ **Rilevamento Zone Intelligente**: Algoritmo per distinguere diversi componenti
- ✅ **Gestione Performance**: Ottimizzazioni per fluidità
- ✅ **Architettura Modulare**: Facile estensione e personalizzazione

## 🎬 Demo

### Setup Rapido
```bash
# 1. Clona il repository
git clone https://github.com/tuonome/druman.git
cd druman

# 2. Setup automatico (Windows)
setup.bat

# 3. Avvia l'applicazione
python main.py
```

### Controlli Base
- **TAB**: Apri/Chiudi menu
- **ESC**: Esci
- **Nel Menu**: M (Metronomo), V (Volume), C (Calibrazione)

## 🚀 Installazione

### Requisiti di Sistema

- **Python**: 3.8 o superiore
- **Webcam**: Qualsiasi webcam USB compatibile
- **RAM**: Minimo 4GB (consigliati 8GB)
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Installazione Automatica

**Windows:**
```bash
setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

### Installazione Manuale

1. **Clona il repository:**
```bash
git clone https://github.com/tuonome/druman.git
cd druman
```

2. **Crea ambiente virtuale:**
```bash
python -m venv venv
```

3. **Attiva ambiente virtuale:**
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Windows (CMD): `venv\Scripts\activate.bat`
   - Linux/macOS: `source venv/bin/activate`

4. **Installa dipendenze:**
```bash
pip install -r requirements.txt
```

### Verifica Installazione

```bash
python test_components.py
```

## 🎮 Utilizzo

### Avvio Base

```bash
python main.py
```

### Simulatore Trigger System

Per vedere tutti i calcoli di trigger, latenza e modulazione:

```bash
python simulator_app.py
```

Il simulatore offre 3 modalità:
1. **Simulazione**: 10 frame con dati simulati
2. **Demo tempo reale**: Demo continua per 10 secondi
3. **Modalità interattiva**: Inserisci valori manualmente per testare

### Esempi di Utilizzo

Per vedere esempi di tutte le funzionalità del TriggerSystem:

```bash
python examples/trigger_examples.py
```

### Prima Volta

1. **Posizionati davanti alla camera** (circa 1-2 metri di distanza)
2. **Assicurati buona illuminazione**
3. **Esegui la calibrazione** (Menu → C → SPACE)
4. **Muoviti naturalmente** per 5 secondi durante la calibrazione

### Controlli Completi

#### Controlli Principali
| Tasto | Azione |
|-------|--------|
| `TAB` | Apri/Chiudi Menu |
| `ESC` | Esci dall'applicazione |

#### Menu Metronomo (M)
| Tasto | Azione |
|-------|--------|
| `SPACE` | Attiva/Disattiva |
| `↑` | Aumenta BPM (+5) |
| `↓` | Diminuisci BPM (-5) |
| `M` | Torna al menu |

#### Menu Volume (V)
| Tasto | Azione |
|-------|--------|
| `↑` | Aumenta volume (+10%) |
| `↓` | Diminuisci volume (-10%) |
| `V` | Torna al menu |

#### Menu Calibrazione (C)
| Tasto | Azione |
|-------|--------|
| `SPACE` | Avvia calibrazione (5 sec) |
| `C` | Torna al menu |

### Zone della Batteria

| Componente | Posizione | Trigger |
|------------|-----------|---------|
| **Kick** | Basso centrale | Piedi (caviglie) |
| **Snare** | Centro | Mani (polsi) |
| **Hi-Hat** | Sinistra alta | Mano sinistra |
| **Crash** | Destra alta | Mano destra |
| **Tom1** | Sinistra centro | Mano sinistra |
| **Tom2** | Destra centro | Mano destra |

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────┐
│                    DrumMan System                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Webcam] → [Motion Tracker] → [Zone Detector]         │
│      ↓              ↓                ↓                   │
│  [Frame]    [Key Points]    [Hit Detection]            │
│      ↓              ↓                ↓                   │
│  [MediaPipe]  [Smoothing]   [Velocity Calc]             │
│                                                          │
│  [Zone Detector] → [Drum Machine] → [Audio Output]      │
│         ↓                ↓              ↓               │
│  [Hit Zones]    [Sound Synthesis]  [Pygame Mixer]       │
│                                                          │
│  [All Components] → [Virtual Environment] → [Display]   │
│         ↓                        ↓           ↓          │
│  [State]              [3D Visualization]  [Pygame]    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Componenti Principali

1. **Motion Tracker** (`src/motion_tracker.py`)
   - Acquisizione video da webcam
   - Pose estimation con MediaPipe
   - Smoothing e calcolo velocità

2. **Zone Detector** (`src/zone_detector.py`)
   - Rilevamento colpi sulle zone
   - Calcolo distanze e velocità relative
   - Gestione cooldown

3. **Drum Machine** (`src/drum_machine.py`)
   - Sintesi audio real-time
   - Generazione suoni con armoniche
   - Metronomo e pattern recording

4. **Virtual Environment** (`src/virtual_environment.py`)
   - Visualizzazione 3D
   - Animazioni e feedback visivo
   - Gestione eventi

5. **Calibration System** (`src/calibration.py`)
   - Calibrazione automatica
   - Normalizzazione posizioni
   - Ottimizzazione tracking

6. **UI Menu** (`src/ui_menu.py`)
   - Menu interattivo
   - Configurazione in-game
   - Gestione callback

## ⚙️ Configurazione

### File di Configurazione

Modifica `src/config.py` per personalizzare:

#### Zone Batteria
```python
DRUM_ZONES = {
    'kick': {
        'center': np.array([0.5, 0.7, 0.0]),  # x, y, z (0-1)
        'radius': 0.15,
        'trigger_distance': 0.2
    },
    # ... altre zone
}
```

#### Audio
```python
SAMPLE_RATE = 44100
MASTER_VOLUME = 0.7
COOLDOWN_TIME = 0.1  # Secondi tra colpi
```

#### Camera
```python
CAMERA_INDEX = 0  # Cambia se hai più camere
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
```

#### Sensibilità
```python
VELOCITY_THRESHOLD = 0.3  # Velocità minima per trigger
```

### Variabili d'Ambiente

Crea un file `.env` (opzionale):
```env
CAMERA_INDEX=0
MASTER_VOLUME=0.7
ENABLE_METRONOME=false
METRONOME_BPM=120
```

## 💻 Sviluppo

### Struttura del Progetto

```
druman/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configurazioni globali
│   ├── motion_tracker.py      # Motion tracking
│   ├── drum_machine.py        # Audio synthesis
│   ├── virtual_environment.py # 3D visualization
│   ├── zone_detector.py       # Hit detection
│   ├── calibration.py         # Calibration system
│   ├── ui_menu.py             # UI menu
│   └── trigger_system.py      # Sistema unificato trigger/latenza
├── examples/
│   └── trigger_examples.py    # Esempi utilizzo TriggerSystem
├── main.py                    # Entry point
├── simulator_app.py          # Simulatore trigger system
├── test_components.py         # Component tests
├── requirements.txt           # Dependencies
├── setup.bat                  # Windows setup
├── setup.sh                   # Linux/macOS setup
├── .gitignore
└── README.md
```

### Estendere il Progetto

#### Aggiungere Nuovi Suoni

Modifica `src/drum_machine.py`:

```python
def _generate_ride(self, duration: float = 0.3) -> np.ndarray:
    """Genera un suono di ride cymbal"""
    # Implementa la sintesi
    return wave

# Aggiungi al dizionario
self.sounds['ride'] = self._generate_ride()
```

#### Aggiungere Nuove Zone

Modifica `src/config.py`:

```python
DRUM_ZONES['ride'] = {
    'center': np.array([0.5, 0.3, 0.0]),
    'radius': 0.10,
    'trigger_distance': 0.15
}
```

#### Personalizzare Visualizzazione

Modifica `src/virtual_environment.py` per cambiare:
- Colori e stili
- Animazioni
- Layout zone

### Test

```bash
# Test tutti i componenti
python test_components.py

# Test specifico
python -c "from src.drum_machine import DrumMachine; d = DrumMachine(); d.play_sound('kick')"
```

## 🔧 Tecnologie

| Componente | Tecnologia | Versione |
|------------|------------|----------|
| **Pose Estimation** | MediaPipe | 0.10.0+ |
| **Computer Vision** | OpenCV | 4.8.0+ |
| **Audio** | Pygame | 2.5.0+ |
| **Signal Processing** | SciPy | 1.11.0+ |
| **Numerical Computing** | NumPy | 1.24.0+ |
| **3D Visualization** | Pygame | 2.5.0+ |

### Dipendenze Principali

- `mediapipe`: Pose estimation real-time
- `opencv-python`: Elaborazione video
- `pygame`: Audio e visualizzazione
- `numpy`: Calcoli numerici
- `scipy`: Elaborazione segnali

## 📊 Performance

### Latenza Stimata

| Componente | Latenza |
|------------|---------|
| Acquisizione frame | 10-30 ms |
| Pose estimation | 15-30 ms |
| Hit detection | 1-2 ms |
| Audio synthesis | 2-5 ms |
| **Totale** | **~30-70 ms** |

### Ottimizzazioni

- ✅ Smoothing efficiente con buffer circolare
- ✅ Cooldown per evitare doppi trigger
- ✅ Generazione audio pre-calcolata
- ✅ Rendering ottimizzato con Pygame

### Requisiti Performance

- **CPU**: Dual-core 2.0GHz+ (consigliato Quad-core)
- **RAM**: 4GB minimo, 8GB consigliato
- **GPU**: Opzionale (MediaPipe usa CPU di default)
- **Camera**: 30 FPS minimo, 60 FPS consigliato

## 🐛 Troubleshooting

### Camera non rilevata

**Problema**: "ERRORE: Impossibile aprire la videocamera"

**Soluzioni**:
1. Verifica che la camera sia collegata
2. Controlla che non sia usata da altre app
3. Cambia `CAMERA_INDEX` in `src/config.py` (prova 1, 2, etc.)
4. Su Linux: verifica permessi `/dev/video0`

### Audio non funziona

**Problema**: Nessun suono

**Soluzioni**:
1. Verifica volume sistema
2. Controlla che Pygame mixer sia inizializzato
3. Su Linux: installa `portaudio19-dev`
4. Verifica che `master_volume > 0` in config

### Performance basse

**Problema**: FPS bassi, lag

**Soluzioni**:
1. Riduci risoluzione camera (`CAMERA_WIDTH/HEIGHT`)
2. Chiudi altre applicazioni pesanti
3. Riduci `history_size` in motion_tracker
4. Disabilita animazioni complesse

### Tracking impreciso

**Problema**: Colpi non rilevati correttamente

**Soluzioni**:
1. Migliora illuminazione
2. Esegui calibrazione (Menu → C)
3. Aumenta `trigger_distance` in config
4. Riduci `VELOCITY_THRESHOLD`

### Import errors

**Problema**: "ModuleNotFoundError"

**Soluzioni**:
1. Verifica ambiente virtuale attivo
2. Reinstalla dipendenze: `pip install -r requirements.txt`
3. Verifica Python 3.8+

## 🗺️ Roadmap

### Versione 1.1 (Prossima)
- [ ] Supporto MIDI output
- [ ] Export pattern in file
- [ ] Più preset di suoni
- [ ] Modalità tutorial

### Versione 1.2
- [ ] Supporto multi-camera
- [ ] Integrazione sensori esterni (opzionale)
- [ ] Recording video + audio
- [ ] Machine learning per migliorare tracking

### Versione 2.0
- [ ] Supporto VR/AR
- [ ] Multiplayer (batteria collaborativa)
- [ ] AI per generazione pattern
- [ ] Integrazione DAW

## 🤝 Contribuire

Contributi sono benvenuti! Per contribuire:

1. **Fork** il repository
2. Crea un **branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** le modifiche (`git commit -m 'Add AmazingFeature'`)
4. **Push** al branch (`git push origin feature/AmazingFeature`)
5. Apri una **Pull Request**

### Linee Guida

- Segui PEP 8 per il codice Python
- Aggiungi docstring alle funzioni
- Testa le modifiche con `test_components.py`
- Aggiorna il README se necessario

## 📄 Licenza

Questo progetto è rilasciato sotto licenza **Educational/Research**.

Libero per uso educativo, ricerca e progetti personali.

## 🙏 Ringraziamenti

- **MediaPipe** per il sistema di pose estimation
- **Pygame** per audio e grafica
- **OpenCV** per elaborazione video
- **NumPy/SciPy** per calcoli scientifici

## 📧 Contatti

- **Issues**: [GitHub Issues](https://github.com/tuonome/druman/issues)
- **Email**: [Il tuo email]

---

<div align="center">

**Divertiti a suonare la tua batteria virtuale! 🥁🎵**

Made with ❤️ for music and technology enthusiasts

[⭐ Star su GitHub](https://github.com/tuonome/druman) | [📖 Documentazione](README.md) | [🐛 Report Bug](https://github.com/tuonome/druman/issues)

</div>
