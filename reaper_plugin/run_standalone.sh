#!/bin/bash
# Avvia l'interfaccia standalone del plugin DrumMan

echo "========================================"
echo "DrumMan Reaper Plugin - Standalone GUI"
echo "========================================"
echo ""

cd "$(dirname "$0")/.."

python3 reaper_plugin/DrumMan_Standalone_GUI.py

