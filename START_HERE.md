# 🚀 START HERE - DrumMan

**Guida rapida per iniziare subito!**

## ⚡ Setup Rapido (3 minuti)

### 1. Installa Dipendenze

**Windows:**
```bash
setup.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh && ./setup.sh
```

### 2. Setup Kit Suoni

```bash
python scripts/download_and_setup_kits.py
```

### 3. Avvia l'App

```bash
python main.py
```

## 🎮 Primi Passi

1. **Posizionati davanti alla webcam** (1-2 metri)
2. **Premi `TAB`** per aprire il menu
3. **Premi `C`** → `SPACE` per calibrare (5 secondi)
4. **Muoviti** come se stessi suonando una batteria!

## ⌨️ Controlli Essenziali

| Tasto | Azione |
|-------|--------|
| `TAB` | Menu |
| `ESC` | Esci |
| `M` (nel menu) | Metronomo |
| `V` (nel menu) | Volume |
| `C` (nel menu) | Calibrazione |

## 🎯 Zone Batteria

- **Kick** (Cassa): Piedi in basso
- **Snare** (Rullante): Mani al centro
- **Hi-Hat**: Mano sinistra in alto
- **Crash**: Mano destra in alto
- **Tom1/Tom2**: Mani a sinistra/destra

## ❓ Problemi?

### Camera non funziona?
- Chiudi altre app che usano la camera
- Cambia `CAMERA_INDEX` in `src/config.py`

### Nessun suono?
- Verifica volume sistema
- Controlla che `USE_SOUND_LIBRARY = True` in `src/config.py`

### Tracking impreciso?
- Migliora illuminazione
- Esegui calibrazione (Menu → C → SPACE)

## 📖 Documentazione Completa

- **Guida Completa**: `GUIDA_USO.md`
- **README**: `README.md`
- **Kit Suoni**: `QUICK_START_KITS.md`
- **Reaper**: `QUICK_START_REAPER.md`

---

**Pronto? Avvia con `python main.py` e inizia a suonare! 🥁**

