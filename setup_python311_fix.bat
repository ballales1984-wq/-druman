@echo off
REM Script per setup Python 3.11 e installazione MediaPipe
REM Versione migliorata con controlli

echo ========================================
echo DrumMan - Setup Python 3.11
echo ========================================
echo.

REM Verifica che siamo nella directory corretta
if not exist "requirements.txt" (
    echo [ERROR] File requirements.txt non trovato!
    echo.
    echo Assicurati di essere nella directory del progetto:
    echo   cd C:\Users\user\tesi\druman
    echo.
    pause
    exit /b 1
)

echo [OK] Directory progetto corretta
echo.

REM Verifica se Python 3.11 è installato
echo Verifica Python 3.11...
python3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.11 non trovato!
    echo.
    echo Provo Python Launcher...
    py -3.11 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python 3.11 non installato!
        echo.
        echo ========================================
        echo INSTALLAZIONE PYTHON 3.11
        echo ========================================
        echo.
        echo 1. Vai su: https://www.python.org/downloads/release/python-3110/
        echo 2. Scarica "Windows installer (64-bit)"
        echo 3. Durante installazione, seleziona "Add Python 3.11 to PATH"
        echo 4. Installa e riavvia questo script
        echo.
        echo Vedi INSTALLA_PYTHON311.md per dettagli
        echo.
        pause
        exit /b 1
    ) else (
        echo [OK] Python 3.11 trovato tramite Python Launcher
        set PYTHON_CMD=py -3.11
    )
) else (
    echo [OK] Python 3.11 trovato!
    set PYTHON_CMD=python3.11
)

echo.
echo ========================================
echo Creazione Ambiente Virtuale
echo ========================================
echo.

REM Rimuovi ambiente esistente se presente
if exist "venv311" (
    echo Rimozione ambiente virtuale esistente...
    rmdir /s /q venv311
)

REM Crea ambiente virtuale
echo Creazione ambiente virtuale Python 3.11...
%PYTHON_CMD% -m venv venv311
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
echo.
echo ========================================
echo Aggiornamento pip
echo ========================================
echo.
python -m pip install --upgrade pip setuptools wheel

REM Installa dipendenze
echo.
echo ========================================
echo Installazione Dipendenze
echo ========================================
echo.
echo Questo potrebbe richiedere alcuni minuti...
echo.

pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [OK] Installazione completata!
    echo ========================================
    echo.
    echo Per usare questo ambiente:
    echo   1. cd C:\Users\user\tesi\druman
    echo   2. venv311\Scripts\activate
    echo   3. python main.py
    echo.
    echo Verifica installazione:
    echo   python check_dependencies.py
    echo.
) else (
    echo.
    echo [ERROR] Errore durante installazione
    echo Controlla i messaggi sopra per dettagli
    echo.
)

pause

