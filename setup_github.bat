@echo off
REM Script per configurare e fare push su GitHub (Windows)

echo ==========================================
echo DrumMan - Setup GitHub Repository
echo ==========================================
echo.

REM Verifica se git è installato
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Git non trovato!
    echo Installa Git da https://git-scm.com/
    pause
    exit /b 1
)

echo Git trovato!
echo.

REM Verifica se siamo in un repository git
if not exist .git (
    echo Inizializzazione repository Git...
    git init
    echo Repository inizializzato!
) else (
    echo Repository Git già esistente!
)

echo.

REM Aggiungi tutti i file
echo Aggiunta file al repository...
git add .

REM Verifica se ci sono modifiche
git diff --staged --quiet >nul 2>&1
if errorlevel 1 (
    REM Ci sono modifiche
    echo.
    set /p commit_msg="Messaggio commit [default: Initial commit]: "
    if "!commit_msg!"=="" set commit_msg=Initial commit
    
    git commit -m "!commit_msg!"
    echo File committati!
) else (
    echo Nessuna modifica da committare
)

echo.

REM Configurazione remote
echo Configurazione remote GitHub...
set /p repo_url="URL repository GitHub (es. https://github.com/tuonome/druman.git): "

if "!repo_url!"=="" (
    echo URL non fornito, salto configurazione remote
) else (
    REM Rimuovi remote esistente se presente
    git remote remove origin 2>nul
    
    REM Aggiungi nuovo remote
    git remote add origin "!repo_url!"
    echo Remote configurato: !repo_url!
    
    echo.
    set /p do_push="Vuoi fare push su GitHub? [s/N]: "
    
    if /i "!do_push!"=="s" (
        echo.
        echo Push su GitHub...
        
        REM Determina branch principale
        for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set main_branch=%%i
        if "!main_branch!"=="" set main_branch=main
        
        REM Crea branch se non esiste
        git checkout -b "!main_branch!" 2>nul
        
        REM Push
        git push -u origin "!main_branch!"
        
        if errorlevel 1 (
            echo Errore durante il push
            echo Verifica le credenziali GitHub e i permessi del repository
        ) else (
            echo Push completato con successo!
        )
    )
)

echo.
echo ==========================================
echo Setup completato!
echo ==========================================
echo.
echo Prossimi passi:
echo 1. Verifica il repository su GitHub
echo 2. Configura GitHub Actions (se necessario)
echo 3. Aggiungi descrizione e README su GitHub
echo 4. Configura GitHub Pages (opzionale)
echo.
pause

