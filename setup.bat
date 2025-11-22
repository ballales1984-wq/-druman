@echo off
echo ========================================
echo DrumMan - Setup Ambiente Virtuale
echo ========================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato!
    echo Installa Python 3.8 o superiore da https://www.python.org/
    pause
    exit /b 1
)

echo Python trovato!
echo.

REM Crea ambiente virtuale
echo Creazione ambiente virtuale...
python -m venv venv
if errorlevel 1 (
    echo ERRORE: Impossibile creare l'ambiente virtuale!
    pause
    exit /b 1
)

echo Ambiente virtuale creato!
echo.

REM Attiva ambiente virtuale
echo Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

REM Aggiorna pip
echo Aggiornamento pip...
python -m pip install --upgrade pip

REM Installa dipendenze
echo.
echo Installazione dipendenze...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRORE: Impossibile installare le dipendenze!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completato con successo!
echo ========================================
echo.
echo Per avviare l'applicazione:
echo   1. Attiva l'ambiente virtuale: venv\Scripts\activate.bat
echo   2. Esegui: python main.py
echo.
pause

