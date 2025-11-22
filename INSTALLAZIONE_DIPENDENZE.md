# 📦 Installazione Dipendenze - DrumMan

## ⚠️ Problemi Rilevati

### Python 3.13
**Problema**: MediaPipe non supporta Python 3.13 (supporta fino a Python 3.12)

**Soluzione**: 
- Usa Python 3.10, 3.11 o 3.12
- Oppure aspetta che MediaPipe aggiunga supporto per Python 3.13

### python-rtmidi
**Problema**: Richiede compilatore C++ (Visual Studio Build Tools)

**Soluzione**:
- Installa Visual Studio Build Tools
- Oppure usa solo MIDI senza rtmidi (funziona con mido)

## ✅ Dipendenze Installate

Le seguenti dipendenze sono state installate con successo:
- ✅ **mido** - Per comunicazione MIDI
- ✅ **python-osc** - Per comunicazione OSC

## 📋 Installazione Completa

### Opzione 1: Usa Python 3.10-3.12 (Consigliato)

1. **Installa Python 3.11 o 3.12** da [python.org](https://www.python.org/downloads/)

2. **Crea ambiente virtuale**:
   ```bash
   python3.11 -m venv venv
   ```

3. **Attiva ambiente**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

4. **Installa tutte le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```

### Opzione 2: Installa Manualmente (Python 3.13)

#### Dipendenze Essenziali
```bash
# Core
pip install numpy opencv-python pygame scipy

# Motion Tracking (NON DISPONIBILE per Python 3.13)
# MediaPipe richiede Python <= 3.12

# Audio
pip install soundfile
```

#### Dipendenze Opzionali (Reaper)
```bash
# MIDI/OSC (già installate)
pip install mido python-osc

# python-rtmidi (richiede compilatore C++)
# Installa Visual Studio Build Tools prima
pip install python-rtmidi
```

### Opzione 3: Installa Visual Studio Build Tools

Per installare `python-rtmidi` su Windows:

1. **Scarica Visual Studio Build Tools**:
   - Vai su: https://visualstudio.microsoft.com/downloads/
   - Scarica "Build Tools for Visual Studio"

2. **Installa**:
   - Seleziona "Desktop development with C++"
   - Installa

3. **Riprova installazione**:
   ```bash
   pip install python-rtmidi
   ```

## 🔍 Verifica Installazione

Esegui lo script di verifica:

```bash
python check_dependencies.py
```

## 📊 Stato Attuale

| Dipendenza | Stato | Note |
|------------|-------|------|
| NumPy | ✅ Installato | |
| OpenCV | ✅ Installato | |
| MediaPipe | ❌ Non disponibile | Richiede Python <= 3.12 |
| Pygame | ✅ Installato | |
| SciPy | ✅ Installato | |
| SoundFile | ✅ Installato | |
| Mido | ✅ Installato | |
| python-rtmidi | ❌ Richiede compilatore | Opzionale |
| python-osc | ✅ Installato | |

## 🚀 Soluzione Rapida

**Per usare DrumMan subito con Python 3.13**:

1. **Installa dipendenze base**:
   ```bash
   pip install numpy opencv-python pygame scipy soundfile mido python-osc
   ```

2. **MediaPipe**: 
   - Usa Python 3.11 o 3.12 per MediaPipe
   - Oppure aspetta supporto Python 3.13

3. **Motion Tracking**:
   - Senza MediaPipe, il motion tracking non funzionerà
   - L'app può funzionare con altri input (MIDI esterno, etc.)

## 💡 Note

- **MediaPipe** è essenziale per il motion tracking. Senza di esso, l'app non può rilevare i movimenti dalla webcam.
- **python-rtmidi** è opzionale. `mido` può funzionare senza di esso per la maggior parte dei casi.
- **python-osc** è già installato e funziona.

## 🔧 Troubleshooting

### MediaPipe non installato
```bash
# Verifica versione Python
python --version

# Se Python 3.13, installa Python 3.11 o 3.12
```

### python-rtmidi errore compilazione
```bash
# Installa Visual Studio Build Tools
# Oppure usa solo mido (funziona per la maggior parte dei casi)
```

### Import errors
```bash
# Verifica ambiente virtuale attivo
# Reinstalla dipendenze
pip install --upgrade -r requirements.txt
```

