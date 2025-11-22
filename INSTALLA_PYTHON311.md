# 🐍 Guida Installazione Python 3.11

## ⚠️ Problema Rilevato

Python 3.11 non è installato sul sistema. MediaPipe richiede Python 3.10, 3.11 o 3.12.

## 📥 Passo 1: Scarica Python 3.11

1. **Vai al sito ufficiale**:
   - Apri browser e vai su: https://www.python.org/downloads/release/python-3110/
   - Oppure: https://www.python.org/downloads/ (cerca Python 3.11)

2. **Scarica installer**:
   - Clicca su "Windows installer (64-bit)" per Windows 64-bit
   - Il file sarà: `python-3.11.0-amd64.exe` (o versione più recente)

## 🔧 Passo 2: Installa Python 3.11

1. **Esegui l'installer** scaricato

2. **IMPORTANTE**: Durante l'installazione:
   - ✅ **Seleziona "Add Python 3.11 to PATH"** (molto importante!)
   - ✅ Seleziona "Install for all users" (opzionale)

3. **Clicca "Install Now"**

4. **Attendi completamento installazione**

5. **Chiudi l'installer**

## ✅ Passo 3: Verifica Installazione

Apri un **NUOVO** terminale (PowerShell o CMD) e verifica:

```cmd
python3.11 --version
```

Dovresti vedere: `Python 3.11.x`

## 🚀 Passo 4: Setup DrumMan con Python 3.11

**IMPORTANTE**: Devi essere nella directory del progetto!

```cmd
cd C:\Users\user\tesi\druman
```

Poi esegui:

```cmd
setup_python311.bat
```

Oppure manualmente:

```cmd
python3.11 -m venv venv311
venv311\Scripts\activate
pip install -r requirements.txt
```

## 📝 Note

- **Chiudi e riapri il terminale** dopo aver installato Python 3.11
- Assicurati di essere nella directory corretta: `C:\Users\user\tesi\druman`
- Se `python3.11` non funziona, prova `py -3.11` (Python Launcher)

## 🔍 Verifica Finale

Dopo installazione, verifica:

```cmd
cd C:\Users\user\tesi\druman
venv311\Scripts\activate
python check_dependencies.py
```

Dovresti vedere MediaPipe installato!

