# DrumMan → Reaper Workflow

## Flusso completo

```
[1. GENERATE]     [2. EXPORT]      [3. IMPORT]     [4. CONFIGURE]
                                                             
Audio/MP3  ──►  MIDI File  ──►  Reaper   ──►  Sampler
(analisi)           (.mid)        (drag)       (ReaSamplOmatic)
```

---

## Step 1: Genera la batteria

### Metodo 1: Da file audio
```bash
python -m src.drum_generator canzone.wav 8 rock medium
```
- Analizza il file audio
- Rileva BPM, stile, groove
- Genera pattern

### Metodo 2: Quick generation (senza audio)
```python
from src.drum_generator import DrumGenerator, MusicStyle

gen = DrumGenerator()
gen.analysis = ...  # manual values or default
pattern = gen.generate_drum_pattern(bars=8, style=MusicStyle.ROCK, complexity='medium')
gen.export_to_midi("drums.mid")
```

---

## Step 2: Importa in Reaper

1. **Apri Reaper**
2. **Trascina** il file `drums.mid` nella traccia desiderata
   - Oppure: `File → Import MIDI file...`

---

## Step 3: Configura il sampler

### Opzione A: ReaSamplOmatic5000 (gratuito)
1. Traccia → Add FX
2. Cerco: `JS: ReaSamplOmatic5000`
3. Load samples:
   - Clicca "Load bank" o trascina file WAV
   - Mappa note (36=kick, 38=snare, 42=hihat, etc.)

### Opzione B: EZdrummer / Superior Drummer
1. Traccia → Add FX
2. Carica il tuo drum kit preferito
3. assegna il MIDI alla traccia

### Opzione C: Virtuali (VSTi)
1. Traccia → Add FX
2. Scegli il tuo instrumento VSTi
3. assegna MIDI

---

## Step 4: Mappatura note MIDI

| Drum | Note MIDI |
|------|----------|
| Kick | 36 (C2) |
| Snare | 38 (D2) |
| Hi-Hat Closed | 42 (F#2) |
| Hi-Hat Open | 46 (A#2) |
| Crash | 49 (C#3) |
| Ride | 51 (D#3) |
| Tom1 | 48 (B2) |
| Tom2 | 45 (A2) |

---

## Quick Test

1. Genera: `python -m src.drum_generator test.wav 4 rock simple`
2. Trova: `outputs/test_simple.mid`
3. Importa in Reaper
4. Aggiungi ReaSamplOmatic5000
5. Carica i tuoi campioni
6. Play!

---

## Troubleshooting

### Nessun suono?
- Verifica che il MIDI sia sulla traccia giusta
- Check: FX > MIDI > Canale

### Suoni sbagliati?
- Cambia mapping nel sampler
- Verifica velocity (il generatore usa velocity 60-127)

### Batteria fuori tempo?
- Verifica BPM nel progetto (120 default)
- Adjust: `gen.analysis.tempo = 140` per più veloce