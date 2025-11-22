# Sistema di Trigger Unificato

## Panoramica

Il `TriggerSystem` è un modulo completo che integra tutte le formule per il calcolo di trigger, latenza e modulazione per un sistema di batteria virtuale.

## Componenti

### 1. Calcolo Latenza Totale

Calcola la latenza totale del sistema sommando le latenze di tutti i componenti:

```python
latenza_totale = lat_microfono + lat_piede + lat_pose + lat_compensativo + lat_drum_machine
```

**Valori Default:**
- Microfono: 3 ms
- Piede: 10 ms
- Pose: 25 ms
- Compensativo: 5 ms
- Drum Machine: 5 ms
- **Totale: ~48 ms**

### 2. Trigger Piede (Accelerometro)

Rileva colpi del piede basandosi sull'accelerazione:

```python
triggered, intensity = trigger_piede(acceleration, soglia=1.5)
```

- **Soglia default**: 1.5 g (gravità)
- **Intensità**: Calcolata normalizzata (0-1)
- **Smoothing**: Media mobile su 3 campioni

### 3. Trigger Mano (Pose Detection)

Rileva movimenti della mano basandosi sulla velocità:

```python
triggered, intensity = trigger_mano(velocita_mano, soglia=0.5)
```

- **Soglia default**: 0.5 (normalizzata)
- **Intensità**: Calcolata normalizzata (0-1)
- **Compensazione latenza**: Calcolata automaticamente

### 4. Trigger Microfono (Superfici)

Rileva colpi su superfici tramite picco audio:

```python
triggered, intensity = trigger_microfono(amplitude, soglia=0.2)
```

- **Soglia default**: 0.2 (normalizzata 0-1)
- **Picco**: Calcolato su buffer recente
- **Intensità**: Basata sul picco

### 5. Modulazione Volume Dinamico

Calcola il volume basandosi sull'intensità del colpo:

```python
volume = calcola_volume(intensita, min_vol=0.2, max_vol=1.0)
```

- **Curva non lineare**: `intensity^0.7` per suono più naturale
- **Range default**: 0.2 - 1.0

### 6. Compensazione Latenza

Compensa la latenza del pose detection basandosi sulla velocità:

```python
compensazione = compensa_latenza_mano(lat_pose, velocita_mano)
```

- **Modello proporzionale**: Più veloce = meno compensazione
- **Limite**: Tra 0 e latenza totale

### 7. Mappatura Suoni

Mappa i trigger ai suoni campionati:

```python
suono = mappa_suono(trigger_type, triggered, intensity)
```

**Mappatura default:**
- `piede` → `kick`
- `mano` → `snare`
- `microfono` → `snare`

### 8. Processamento Unificato

Processa tutti i trigger insieme:

```python
risultati = processa_trigger_unificato(
    acceleration_piede=2.0,
    velocita_mano=0.7,
    amplitude_microfono=0.15
)
```

Restituisce:
- Latenza totale
- Stato di tutti i trigger
- Suoni generati con volume e intensità

## Utilizzo

### Esempio Base

```python
from src.trigger_system import TriggerSystem

# Inizializza
trigger_sys = TriggerSystem()

# Processa trigger
risultati = trigger_sys.processa_trigger_unificato(
    acceleration_piede=2.0,
    velocita_mano=0.7,
    amplitude_microfono=0.15
)

# Usa risultati
for suono in risultati['suoni']:
    print(f"Suona {suono['sound']} a volume {suono['volume']}")
```

### Personalizzazione

```python
# Cambia soglie
trigger_sys.thresholds['piede'] = 2.0
trigger_sys.thresholds['mano'] = 0.6

# Cambia latenze
trigger_sys.latencies['pose'] = 30

# Cambia range volume
trigger_sys.volume_range = {'min': 0.3, 'max': 0.9}
```

## Simulatore

Usa `simulator_app.py` per vedere tutti i calcoli in azione:

```bash
python simulator_app.py
```

Modalità disponibili:
1. **Simulazione**: Frame simulati con dati casuali
2. **Demo tempo reale**: Demo continua
3. **Interattiva**: Input manuale per test

## Esempi

Vedi `examples/trigger_examples.py` per esempi completi di tutte le funzionalità.

## Performance

- **Latenza totale**: ~30-70 ms (accettabile per live)
- **Overhead**: Minimo (calcoli semplici)
- **Buffer**: Piccoli buffer circolari per smoothing

## Estensione

Per aggiungere nuovi tipi di trigger:

1. Aggiungi metodo `trigger_*()` in `TriggerSystem`
2. Aggiungi al `processa_trigger_unificato()`
3. Aggiorna mappatura suoni se necessario

