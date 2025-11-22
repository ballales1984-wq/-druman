"""
Script per verificare tutte le dipendenze
"""
import sys

print("="*60)
print("DrumMan - Verifica Dipendenze")
print("="*60)
print()

# Core dependencies
dependencies = {
    'numpy': 'NumPy',
    'cv2': 'OpenCV',
    'mediapipe': 'MediaPipe',
    'pygame': 'Pygame',
    'scipy': 'SciPy',
    'soundfile': 'SoundFile',
    'mido': 'Mido (MIDI)',
    'rtmidi': 'python-rtmidi',
    'pythonosc': 'python-osc'
}

missing = []
installed = []

for module, name in dependencies.items():
    try:
        if module == 'cv2':
            import cv2
            print(f"[OK] {name}: {cv2.__version__}")
        elif module == 'mediapipe':
            import mediapipe as mp
            print(f"[OK] {name}: {mp.__version__}")
        elif module == 'pygame':
            import pygame
            print(f"[OK] {name}: {pygame.version.ver}")
        elif module == 'numpy':
            import numpy
            print(f"[OK] {name}: {numpy.__version__}")
        elif module == 'scipy':
            import scipy
            print(f"[OK] {name}: {scipy.__version__}")
        elif module == 'soundfile':
            import soundfile
            print(f"[OK] {name}: OK")
        elif module == 'mido':
            import mido
            # mido non ha __version__
            print(f"[OK] {name}: OK")
        elif module == 'rtmidi':
            import rtmidi
            print(f"[OK] {name}: OK")
        elif module == 'pythonosc':
            from pythonosc import osc_message_builder
            print(f"[OK] {name}: OK")
        else:
            __import__(module)
            print(f"[OK] {name}: OK")
        installed.append(name)
    except ImportError:
        print(f"[MISSING] {name}: NON INSTALLATO")
        missing.append(name)

print()
print("="*60)
print("Riepilogo")
print("="*60)
print(f"Installate: {len(installed)}/{len(dependencies)}")
print(f"Mancanti: {len(missing)}/{len(dependencies)}")

if missing:
    print()
    print("Dipendenze mancanti:")
    for dep in missing:
        print(f"  - {dep}")
    print()
    print("Installa con:")
    print("  pip install -r requirements.txt")

# Verifica import moduli progetto
print()
print("="*60)
print("Verifica Moduli Progetto")
print("="*60)

modules = [
    'src.config',
    'src.drum_machine',
    'src.sound_library',
    'src.reaper_connector'
]

for module in modules:
    try:
        __import__(module)
        print(f"[OK] {module}")
    except ImportError as e:
        print(f"[ERROR] {module}: {e}")

print()
print("="*60)
print("Verifica Completata")
print("="*60)

