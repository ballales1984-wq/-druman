# 🎯 Configurazione Pad in Colonna - DrumMan

## ✨ Modifiche Implementate

### 1. Pad in Colonna Verticale
I pad sono ora disposti in **colonna verticale** al centro dello schermo, basandosi sull'**altezza delle mani** (coordinata Y).

### 2. Rilevamento Basato su Altezza
Il sistema rileva i colpi basandosi **solo sull'altezza** (Y), ignorando la posizione orizzontale (X).

## 📊 Layout Pad

I pad sono disposti dall'**alto al basso**:

| Pad | Altezza (Y) | Range Trigger | Posizione |
|-----|-------------|---------------|-----------|
| **Crash** | 0.15 (Alto) | 0.0 - 0.25 | Mani molto in alto |
| **Hi-Hat** | 0.30 | 0.20 - 0.40 | Mani alte |
| **Tom2** | 0.50 (Medio) | 0.40 - 0.60 | Mani a media altezza |
| **Snare** | 0.70 | 0.60 - 0.80 | Mani medio-basse |
| **Tom1** | 0.85 | 0.75 - 0.95 | Mani basse |
| **Kick** | 0.95 (Basso) | 0.85 - 1.0 | Piedi (caviglie) |

## 🎮 Come Funziona

### Rilevamento
- **Mani**: L'altezza delle mani (coordinata Y) determina quale pad viene attivato
- **Piedi**: L'altezza dei piedi attiva il kick
- **X ignorato**: La posizione orizzontale non conta, solo l'altezza

### Visualizzazione
- Pad rettangolari verticali al centro dello schermo
- Larghezza: 25% della larghezza video
- Altezza: Basata sul range di trigger
- Colore verde quando attivo

## ⚙️ Personalizzazione

### Modificare Range Altezza

In `src/config.py`, modifica `height_range`:

```python
'crash': {
    'center': np.array([0.5, 0.15, 0.0]),
    'height_range': (0.0, 0.25)  # Modifica qui per cambiare range
}
```

### Modificare Posizione Pad

Cambia la coordinata Y in `center`:

```python
'crash': {
    'center': np.array([0.5, 0.20, 0.0]),  # Cambia 0.20 per spostare più in basso
    ...
}
```

### Modificare Larghezza Pad

In `src/video_overlay.py`, modifica:

```python
pad_width = int(self.camera_width * 0.25)  # Cambia 0.25 per larghezza diversa
```

## 💡 Suggerimenti

1. **Posizionamento**: Stai a 1-2 metri dalla camera
2. **Altezza**: Muovi le mani dall'alto al basso per attivare diversi pad
3. **Calibrazione**: Esegui calibrazione (Menu → C) per migliorare precisione
4. **Distanza**: Se i pad non si attivano, potresti essere troppo vicino/lontano

## 🔧 Troubleshooting

### Pad non si attivano
- Verifica che le mani siano nel range di altezza corretto
- Controlla che la velocità sia sufficiente (`VELOCITY_THRESHOLD`)
- Esegui calibrazione

### Pad si attivano troppo facilmente
- Aumenta `VELOCITY_THRESHOLD` in `src/config.py`
- Riduci i range in `height_range`

### Pad sovrapposti
- I pad ora sono in colonna, non dovrebbero sovrapporsi
- Se ancora sovrapposti, riduci i range in `height_range`

## 📝 Note

- I pad sono sempre al centro orizzontale (X = 0.5)
- Solo l'altezza (Y) determina quale pad viene attivato
- La posizione orizzontale (X) è ignorata per il rilevamento
- Questo sistema è più intuitivo e evita sovrapposizioni

