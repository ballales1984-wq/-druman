@echo off
REM Script principale per avviare setup Python 3.11
REM Questo script naviga nella directory corretta e avvia setup

echo ========================================
echo DrumMan - Avvio Setup
echo ========================================
echo.

REM Vai nella directory del progetto
cd /d "%~dp0"

REM Verifica che siamo nella directory corretta
if not exist "requirements.txt" (
    echo [ERROR] File requirements.txt non trovato!
    echo Directory corrente: %CD%
    echo.
    echo Assicurati di eseguire questo script dalla directory del progetto.
    pause
    exit /b 1
)

echo [OK] Directory progetto: %CD%
echo.

REM Verifica se Python 3.11 è disponibile
python3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python 3.11 trovato!
    echo.
    call setup_python311_fix.bat
) else (
    py -3.11 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Python 3.11 trovato tramite Python Launcher!
        echo.
        call setup_python311_fix.bat
    ) else (
        echo [ERROR] Python 3.11 non trovato!
        echo.
        echo ========================================
        echo INSTALLA PYTHON 3.11 PRIMA
        echo ========================================
        echo.
        echo 1. Vai su: https://www.python.org/downloads/release/python-3110/
        echo 2. Scarica "Windows installer (64-bit)"
        echo 3. Durante installazione: SELEZIONA "Add Python 3.11 to PATH"
        echo 4. Installa
        echo 5. CHIUDI e RIAPRI questo terminale
        echo 6. Esegui di nuovo: AVVIA_SETUP.bat
        echo.
        echo Vedi INSTALLA_PYTHON311.md per dettagli completi
        echo.
        pause
    )
)

