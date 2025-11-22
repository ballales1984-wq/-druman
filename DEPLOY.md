# Guida al Deploy su GitHub

## Prerequisiti

1. Account GitHub
2. Git installato sul sistema
3. Repository creato su GitHub (opzionale, lo script può crearlo)

## Setup Automatico

### Windows
```bash
setup_github.bat
```

### Linux/macOS
```bash
chmod +x setup_github.sh
./setup_github.sh
```

## Setup Manuale

### 1. Inizializza Repository (se non già fatto)
```bash
git init
```

### 2. Aggiungi File
```bash
git add .
```

### 3. Commit Iniziale
```bash
git commit -m "Initial commit - DrumMan Virtual Drum Machine"
```

### 4. Crea Repository su GitHub
- Vai su https://github.com/new
- Crea un nuovo repository (es. `druman`)
- **NON** inizializzare con README, .gitignore o license (già presenti)

### 5. Collega Repository Locale a GitHub
```bash
git remote add origin https://github.com/TUO_USERNAME/druman.git
```

### 6. Push su GitHub
```bash
git branch -M main
git push -u origin main
```

## Configurazioni GitHub

### 1. Repository Settings
- Vai su Settings del repository
- Configura:
  - Description: "Virtual Drum Machine with Motion Tracking"
  - Topics: `python`, `drum-machine`, `motion-tracking`, `mediapipe`, `computer-vision`
  - Website: (opzionale)
  - Visibility: Private/Public (a tua scelta)

### 2. GitHub Actions
Le GitHub Actions sono già configurate in `.github/workflows/`:
- **python.yml**: CI/CD per test Python
- **codeql-analysis.yml**: Analisi sicurezza

### 3. Branch Protection (Opzionale)
- Settings → Branches
- Aggiungi regole per `main`:
  - Require pull request reviews
  - Require status checks to pass

### 4. GitHub Pages (Opzionale)
Se vuoi pubblicare documentazione:
```bash
# Settings → Pages
# Source: Deploy from a branch
# Branch: main /docs
```

## Comandi Utili

### Aggiungere Modifiche
```bash
git add .
git commit -m "Descrizione modifiche"
git push
```

### Creare Branch
```bash
git checkout -b feature/nuova-funzionalita
git push -u origin feature/nuova-funzionalita
```

### Tag per Release
```bash
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

### Aggiornare da GitHub
```bash
git pull origin main
```

## Troubleshooting

### Errore: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/TUO_USERNAME/druman.git
```

### Errore: "failed to push"
- Verifica credenziali GitHub
- Usa Personal Access Token se necessario
- Verifica permessi repository

### Errore: "refusing to merge unrelated histories"
```bash
git pull origin main --allow-unrelated-histories
```

## Sicurezza

⚠️ **IMPORTANTE**: Prima di fare push, verifica che:
- Non ci siano credenziali nel codice
- File sensibili siano in `.gitignore`
- LICENSE sia corretta (proprietaria)

## Prossimi Passi

1. ✅ Push completato
2. ⬜ Configura GitHub Actions
3. ⬜ Aggiungi descrizione repository
4. ⬜ Crea prima release
5. ⬜ Configura GitHub Pages (opzionale)

