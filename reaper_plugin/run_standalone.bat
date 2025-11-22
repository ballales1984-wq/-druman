@echo off
REM Avvia l'interfaccia standalone del plugin DrumMan

echo ========================================
echo DrumMan Reaper Plugin - Standalone GUI
echo ========================================
echo.

cd /d %~dp0\..

python reaper_plugin/DrumMan_Standalone_GUI.py

pause

