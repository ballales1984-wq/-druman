# 🥁 DrumMan - Virtual Drum Machine

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](LICENSE)

> Trasforma i tuoi movimenti in suoni di batteria usando computer vision e sintesi audio in tempo reale.

## 🚀 Quick Start

```bash
# Setup automatico
setup.bat  # Windows
./setup.sh # Linux/macOS

# Avvia
python main.py
```

## ✨ Features

- 🎥 **Motion Tracking**: Rilevamento movimenti con webcam (MediaPipe)
- 🥁 **6 Componenti**: Kick, Snare, Hi-Hat, Crash, Tom1, Tom2
- 🎵 **Metronomo**: BPM configurabile (60-200)
- 🎮 **Visualizzazione 3D**: Ambiente virtuale interattivo
- ⚙️ **Calibrazione**: Ottimizzazione automatica del tracking
- 🎛️ **Menu Interattivo**: Configurazione in-game

## 📋 Requisiti

- Python 3.8+
- Webcam USB
- 4GB RAM (8GB consigliato)

## 🎮 Controlli

| Tasto | Azione |
|-------|--------|
| `TAB` | Menu |
| `ESC` | Esci |
| `M` | Metronomo (nel menu) |
| `V` | Volume (nel menu) |
| `C` | Calibrazione (nel menu) |

## 📦 Installazione

```bash
git clone https://github.com/tuonome/druman.git
cd druman
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 🏗️ Architettura

```
Webcam → MediaPipe → Zone Detection → Drum Machine → Audio
                ↓
        Virtual Environment → 3D Display
```

## 📖 Documentazione

Vedi [README.md](README.md) per documentazione completa.

## 🤝 Contribuire

Pull requests sono benvenuti! Apri un issue per discussioni.

## 📄 Licenza

Educational/Research - Libero per uso educativo e ricerca.

---

⭐ **Star su GitHub** se ti piace il progetto!

