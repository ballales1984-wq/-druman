@echo off
REM Script per setup Python 3.11 e installazione MediaPipe
echo ========================================
echo DrumMan - Setup Python 3.11
echo ========================================
echo.

REM Verifica se Python 3.11 è installato
python3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.11 non trovato!
    echo.
    echo Installa Python 3.11:
    echo 1. Vai su: https://www.python.org/downloads/
    echo 2. Scarica Python 3.11.x
    echo 3. Durante installazione, seleziona "Add Python to PATH"
    echo 4. Riavvia questo script
    echo.
    pause
    exit /b 1
)

echo [OK] Python 3.11 trovato!
echo.

REM Crea ambiente virtuale
echo Creazione ambiente virtuale Python 3.11...
python3.11 -m venv venv311
if %errorlevel% neq 0 (
    echo [ERROR] Errore creazione ambiente virtuale
    pause
    exit /b 1
)

echo [OK] Ambiente virtuale creato!
echo.

REM Attiva ambiente
echo Attivazione ambiente virtuale...
call venv311\Scripts\activate.bat

REM Aggiorna pip
echo Aggiornamento pip...
python -m pip install --upgrade pip

REM Installa dipendenze
echo Installazione dipendenze...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [OK] Installazione completata!
    echo ========================================
    echo.
    echo Per usare questo ambiente:
    echo   venv311\Scripts\activate
    echo   python main.py
    echo.
) else (
    echo.
    echo [ERROR] Errore durante installazione
    echo.
)

pause

