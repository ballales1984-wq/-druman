"""
Script per provare alternative a MediaPipe su Python 3.13
"""
import sys
import subprocess

print("="*60)
print("MediaPipe - Installazione Alternativa")
print("="*60)
print()

# Verifica versione Python
python_version = sys.version_info
print(f"Python: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major == 3 and python_version.minor >= 13:
    print("\n[WARN] Python 3.13 non è supportato ufficialmente da MediaPipe")
    print("MediaPipe supporta Python 3.8-3.12")
    print()
    print("Opzioni:")
    print("1. Usa Python 3.11 o 3.12 (consigliato)")
    print("2. Prova installazione da sorgente (non garantito)")
    print("3. Usa alternativa: OpenPose o altri tracker")
    print()
    
    # Prova a vedere se ci sono build disponibili
    print("Verifica build disponibili...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", "mediapipe"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(result.stdout)
    except:
        print("Non è possibile verificare versioni disponibili")
    
    print("\n" + "="*60)
    print("Soluzione Consigliata: Python 3.11 o 3.12")
    print("="*60)
    print()
    print("1. Scarica Python 3.11 da: https://www.python.org/downloads/")
    print("2. Installa Python 3.11 (seleziona 'Add to PATH')")
    print("3. Crea nuovo ambiente virtuale:")
    print("   python3.11 -m venv venv311")
    print("4. Attiva ambiente:")
    print("   venv311\\Scripts\\activate  (Windows)")
    print("   source venv311/bin/activate  (Linux/macOS)")
    print("5. Installa dipendenze:")
    print("   pip install -r requirements.txt")
    print()
else:
    print("\n[OK] Versione Python supportata!")
    print("Procedi con: pip install mediapipe")

