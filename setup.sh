#!/bin/bash

echo "========================================"
echo "DrumMan - Setup Ambiente Virtuale"
echo "========================================"
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "ERRORE: Python3 non trovato!"
    echo "Installa Python 3.8 o superiore"
    exit 1
fi

echo "Python trovato!"
echo ""

# Crea ambiente virtuale
echo "Creazione ambiente virtuale..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERRORE: Impossibile creare l'ambiente virtuale!"
    exit 1
fi

echo "Ambiente virtuale creato!"
echo ""

# Attiva ambiente virtuale
echo "Attivazione ambiente virtuale..."
source venv/bin/activate

# Aggiorna pip
echo "Aggiornamento pip..."
python -m pip install --upgrade pip

# Installa dipendenze
echo ""
echo "Installazione dipendenze..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRORE: Impossibile installare le dipendenze!"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup completato con successo!"
echo "========================================"
echo ""
echo "Per avviare l'applicazione:"
echo "  1. Attiva l'ambiente virtuale: source venv/bin/activate"
echo "  2. Esegui: python main.py"
echo ""

