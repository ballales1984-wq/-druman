#!/bin/bash

# Script per configurare e fare push su GitHub

echo "=========================================="
echo "DrumMan - Setup GitHub Repository"
echo "=========================================="
echo ""

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verifica se git è installato
if ! command -v git &> /dev/null; then
    echo -e "${RED}ERRORE: Git non trovato!${NC}"
    echo "Installa Git da https://git-scm.com/"
    exit 1
fi

echo -e "${GREEN}✓ Git trovato${NC}"
echo ""

# Verifica se siamo in un repository git
if [ ! -d .git ]; then
    echo "Inizializzazione repository Git..."
    git init
    echo -e "${GREEN}✓ Repository inizializzato${NC}"
else
    echo -e "${GREEN}✓ Repository Git già esistente${NC}"
fi

echo ""

# Aggiungi tutti i file
echo "Aggiunta file al repository..."
git add .

# Verifica se ci sono modifiche
if git diff --staged --quiet; then
    echo -e "${YELLOW}⚠ Nessuna modifica da committare${NC}"
else
    # Commit
    echo ""
    read -p "Messaggio commit [default: Initial commit]: " commit_msg
    commit_msg=${commit_msg:-"Initial commit"}
    
    git commit -m "$commit_msg"
    echo -e "${GREEN}✓ File committati${NC}"
fi

echo ""

# Configurazione remote
echo "Configurazione remote GitHub..."
read -p "URL repository GitHub (es. https://github.com/tuonome/druman.git): " repo_url

if [ -z "$repo_url" ]; then
    echo -e "${YELLOW}⚠ URL non fornito, salto configurazione remote${NC}"
else
    # Rimuovi remote esistente se presente
    git remote remove origin 2>/dev/null
    
    # Aggiungi nuovo remote
    git remote add origin "$repo_url"
    echo -e "${GREEN}✓ Remote configurato: $repo_url${NC}"
    
    echo ""
    read -p "Vuoi fare push su GitHub? [s/N]: " do_push
    
    if [[ $do_push =~ ^[Ss]$ ]]; then
        echo ""
        echo "Push su GitHub..."
        
        # Determina branch principale
        main_branch=$(git branch --show-current 2>/dev/null || echo "main")
        
        # Crea branch se non esiste
        if ! git rev-parse --verify "$main_branch" >/dev/null 2>&1; then
            git checkout -b "$main_branch"
        fi
        
        # Push
        git push -u origin "$main_branch"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Push completato con successo!${NC}"
        else
            echo -e "${RED}✗ Errore durante il push${NC}"
            echo "Verifica le credenziali GitHub e i permessi del repository"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Setup completato!"
echo "=========================================="
echo ""
echo "Prossimi passi:"
echo "1. Verifica il repository su GitHub"
echo "2. Configura GitHub Actions (se necessario)"
echo "3. Aggiungi descrizione e README su GitHub"
echo "4. Configura GitHub Pages (opzionale)"
echo ""

