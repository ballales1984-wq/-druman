# 🎉 Nuove Funzionalità - DrumMan

## ✨ Cosa è stato aggiunto

### 1. 🎥 Video Overlay Mode
Invece dell'ambiente 3D, ora puoi vedere il **video live della webcam** con overlay dei pad (come i rettangoli verdi del machine learning).

### 2. 🎤 Modalità Beatbox
Rileva suoni vocali beatbox (boom, tss, kick, etc.) e li mappa automaticamente ai suoni della libreria!

## 🚀 Come Usare

### Video Overlay Mode

Modifica `src/config.py`:

```python
USE_VIDEO_OVERLAY = True  # True = video live, False = ambiente 3D
```

**Caratteristiche**:
- Video live della webcam (specchiato)
- Rettangoli verdi per pad attivi
- Etichette con nomi dei componenti
- Informazioni FPS e pad attivi

### Modalità Beatbox

Modifica `src/config.py`:

```python
BEATBOX_MODE = True  # Abilita beatbox vocale
USE_VIDEO_OVERLAY = True  # Consigliato con beatbox
```

**Come funziona**:
1. Il microfono registra continuamente
2. Il programma analizza le frequenze
3. Rileva pattern vocali (boom, tss, etc.)
4. Mappa ai suoni della batteria
5. Suona il suono corrispondente

**Suoni riconosciuti**:
- **boom, bum, boot** → Kick
- **tss, ts, ch** → Snare
- **t, tick** → Hi-Hat
- **tsss, sh** → Crash
- **doom, dom** → Tom1
- **tak, tack** → Tom2

## 📁 File Creati

- `src/video_overlay.py` - Visualizzazione video live con overlay
- `src/beatbox_detector.py` - Rilevamento suoni beatbox vocali
- `BEATBOX_MODE.md` - Documentazione completa beatbox

## ⚙️ Configurazione

### Video Overlay

```python
# src/config.py
USE_VIDEO_OVERLAY = True  # Abilita video overlay
```

### Beatbox

```python
# src/config.py
BEATBOX_MODE = True  # Abilita beatbox
USE_VIDEO_OVERLAY = True  # Consigliato
```

### Soglia Beatbox

Modifica in `src/beatbox_detector.py`:

```python
threshold: float = 0.3  # Soglia rilevamento (0-1)
# Più basso = più sensibile
```

## 🎯 Esempi di Uso

### Solo Video Overlay (Motion Tracking)

```python
USE_VIDEO_OVERLAY = True
BEATBOX_MODE = False
```

### Solo Beatbox

```python
USE_VIDEO_OVERLAY = True
BEATBOX_MODE = True
```

### Entrambi (Futuro)

Puoi combinare motion tracking + beatbox per controllo completo!

## 💡 Suggerimenti

### Video Overlay
- Migliore per vedere te stesso mentre suoni
- Più intuitivo per principianti
- Rettangoli verdi mostrano chiaramente i pad attivi

### Beatbox
- Usa microfono di buona qualità
- Riduci rumore di fondo
- Pronuncia chiaramente i suoni
- Lascia pause tra i suoni

## 🔧 Troubleshooting

### Video non si vede
- Verifica che la webcam sia collegata
- Controlla `CAMERA_INDEX` in config

### Beatbox non rileva
- Verifica microfono
- Controlla volume sistema
- Riduci `threshold` in `beatbox_detector.py`

### Latenza audio
- Riduci `chunk_size` (ma aumenta CPU)
- Chiudi altre app audio

## 📊 Statistiche

Il beatbox detector traccia:
- Rilevamenti totali
- Rilevamenti per componente
- Stato registrazione

Vedi `BEATBOX_MODE.md` per dettagli completi!

