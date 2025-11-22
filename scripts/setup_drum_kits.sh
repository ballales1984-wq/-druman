#!/bin/bash
# Script per setup automatico kit suoni

echo "========================================"
echo "DrumMan - Setup Kit Suoni"
echo "========================================"
echo ""

# Crea directory
mkdir -p sounds/kits

# Genera kit base sintetizzato
echo "1. Generazione kit base sintetizzato..."
python scripts/create_basic_drum_kit.py

echo ""
echo "2. Per scaricare kit online:"
echo "   python download_drum_kits.py list"
echo "   python download_drum_kits.py download <kit_id>"
echo ""
echo "✅ Setup completato!"

