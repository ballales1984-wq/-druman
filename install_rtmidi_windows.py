"""
Script per installare python-rtmidi su Windows
"""
import sys
import subprocess
import os

print("="*60)
print("python-rtmidi - Installazione Windows")
print("="*60)
print()

# Verifica se Visual Studio Build Tools sono installati
print("Verifica compilatore C++...")

# Cerca cl.exe (compilatore Visual Studio)
vs_paths = [
    r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
    r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
    r"C:\Program Files\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC",
    r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC",
]

compiler_found = False
for vs_path in vs_paths:
    if os.path.exists(vs_path):
        print(f"[OK] Visual Studio trovato: {vs_path}")
        compiler_found = True
        break

if not compiler_found:
    print("[WARN] Compilatore C++ non trovato")
    print()
    print("="*60)
    print("Installazione Visual Studio Build Tools")
    print("="*60)
    print()
    print("Opzione 1: Download Manuale")
    print("1. Vai su: https://visualstudio.microsoft.com/downloads/")
    print("2. Scarica 'Build Tools for Visual Studio 2022'")
    print("3. Installa e seleziona 'Desktop development with C++'")
    print("4. Riavvia terminale e riprova: pip install python-rtmidi")
    print()
    print("Opzione 2: Usa solo mido (alternativa)")
    print("- mido funziona senza python-rtmidi per la maggior parte dei casi")
    print("- python-rtmidi è opzionale per migliori performance MIDI")
    print()
    print("Opzione 3: Prova installazione precompilata")
    print("Provo a installare da wheel precompilato...")
    print()
    
    # Prova a installare da wheel precompilato
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "python-rtmidi", "--only-binary", ":all:"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("[OK] python-rtmidi installato da wheel precompilato!")
        else:
            print("[ERROR] Installazione fallita")
            print(result.stderr)
    except Exception as e:
        print(f"[ERROR] Errore: {e}")
        print()
        print("Soluzione: Installa Visual Studio Build Tools")
else:
    print()
    print("Provo installazione python-rtmidi...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "python-rtmidi"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("[OK] python-rtmidi installato con successo!")
        else:
            print("[ERROR] Installazione fallita")
            print(result.stderr)
    except Exception as e:
        print(f"[ERROR] Errore: {e}")

print()
print("="*60)
print("Nota: python-rtmidi è opzionale")
print("="*60)
print("mido funziona senza python-rtmidi per la maggior parte dei casi.")
print("python-rtmidi offre solo migliori performance MIDI.")

