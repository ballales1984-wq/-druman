# 🎤 Modalità Beatbox - DrumMan

## 🎯 Descrizione

La modalità Beatbox permette di suonare la batteria usando la **voce** invece dei movimenti del corpo. Il programma rileva i suoni vocali tipici del beatbox (boom, tss, kick, etc.) e li mappa automaticamente ai suoni della libreria.

## 🎵 Suoni Riconosciuti

| Suono Vocale | Componente Batteria | Esempi |
|--------------|---------------------|--------|
| **boom, bum, boot** | Kick (Cassa) | "boom", "bum", "boot", "b", "p" |
| **tss, ts, ch** | Snare (Rullante) | "tss", "ts", "ch", "chh", "t", "k" |
| **t, ts, tick** | Hi-Hat | "t", "ts", "tss", "ch", "tick" |
| **tsss, sh, crash** | Crash | "tsss", "chhh", "sh", "shh" |
| **doom, dom, dum** | Tom1 | "doom", "dom", "dum", "tom" |
| **tak, tack, tik** | Tom2 | "tak", "tack", "tik", "tick" |

## 🚀 Come Usare

### 1. Abilita Modalità Beatbox

Modifica `src/config.py`:

```python
BEATBOX_MODE = True  # Abilita beatbox
USE_VIDEO_OVERLAY = True  # Mostra video live
```

### 2. Avvia l'App

```bash
python main.py
```

### 3. Canta i Suoni

- **Kick**: Di' "boom", "bum" o "boot"
- **Snare**: Di' "tss", "ts" o "ch"
- **Hi-Hat**: Di' "t" o "tick"
- **Crash**: Di' "tsss" o "sh"
- **Tom**: Di' "doom" o "tak"

## ⚙️ Configurazione

### Soglia di Rilevamento

Modifica in `src/beatbox_detector.py`:

```python
threshold: float = 0.3  # Soglia per rilevamento (0-1)
# Più basso = più sensibile
# Più alto = meno sensibile
```

### Cooldown

```python
cooldown_time = 0.1  # Secondi tra rilevamenti (evita doppi trigger)
```

## 🎛️ Come Funziona

1. **Registrazione Audio**: Il microfono registra continuamente
2. **Analisi Frequenze**: FFT analizza le frequenze del suono
3. **Riconoscimento Pattern**: Confronta con pattern caratteristici
4. **Mappatura**: Mappa il suono vocale al componente batteria
5. **Riproduzione**: Suona il suono corrispondente dalla libreria

## 📊 Statistiche

Il detector traccia:
- Numero totale di rilevamenti
- Rilevamenti per componente
- Stato registrazione

## 💡 Suggerimenti

1. **Microfono**: Usa un microfono di buona qualità per migliori risultati
2. **Ambiente**: Riduci rumore di fondo
3. **Volume**: Parla/canta con volume normale
4. **Pronuncia**: Pronuncia chiaramente i suoni
5. **Timing**: Lascia pause tra i suoni per evitare confusione

## 🔧 Troubleshooting

### Nessun rilevamento
- Verifica che il microfono sia collegato
- Controlla volume sistema
- Riduci `threshold` in `beatbox_detector.py`

### Rilevamenti errati
- Aumenta `threshold`
- Pronuncia più chiaramente
- Modifica `FREQUENCY_RANGES` per i tuoi suoni

### Latenza
- Riduci `chunk_size` (ma aumenta carico CPU)
- Chiudi altre applicazioni audio

## 🎨 Visualizzazione

In modalità beatbox con `USE_VIDEO_OVERLAY = True`:
- Video live della webcam
- Rettangoli verdi per pad attivi
- Informazioni FPS e rilevamenti

## 🔄 Combinazione con Motion Tracking

Puoi usare entrambi contemporaneamente:
- Motion tracking per mani/piedi
- Beatbox per suoni vocali aggiuntivi

Modifica il codice per abilitare entrambi!

