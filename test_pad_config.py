"""Test configurazione pad"""
from src.config import DRUM_ZONES

print("="*60)
print("Configurazione Pad in Colonna")
print("="*60)
print()

for name, zone in DRUM_ZONES.items():
    center = zone['center']
    height_range = zone.get('height_range', 'N/A')
    print(f"{name.upper():10} - Y: {center[1]:.2f} - Range: {height_range}")

print()
print("="*60)
print("Layout:")
print("="*60)
print("ALTO    -> Crash (Y: 0.15, Range: 0.0-0.25)")
print("        -> Hi-Hat (Y: 0.30, Range: 0.20-0.40)")
print("MEDIO   -> Tom2 (Y: 0.50, Range: 0.40-0.60)")
print("        -> Snare (Y: 0.70, Range: 0.60-0.80)")
print("BASSO   -> Tom1 (Y: 0.85, Range: 0.75-0.95)")
print("        -> Kick (Y: 0.95, Range: 0.85-1.0)")
print()
print("I pad sono in colonna verticale al centro!")
print("Solo l'altezza (Y) determina quale pad viene attivato.")

