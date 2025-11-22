"""
Esempi di utilizzo del TriggerSystem
Mostra come usare tutte le funzionalità del sistema di trigger
"""
from src.trigger_system import TriggerSystem
import time

def esempio_latenza():
    """Esempio: Calcolo latenza totale"""
    print("=" * 60)
    print("ESEMPIO 1: Calcolo Latenza Totale")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Latenza con valori default
    latenza_default = trigger_sys.calcola_latenza_totale()
    print(f"Latenza totale (default): {latenza_default} ms")
    
    # Latenza con valori personalizzati
    latenza_custom = trigger_sys.calcola_latenza_totale(
        lat_microfono=2,
        lat_piede=8,
        lat_pose=20,
        lat_compensativo=3,
        lat_drum_machine=4
    )
    print(f"Latenza totale (custom): {latenza_custom} ms")
    print()

def esempio_trigger_piede():
    """Esempio: Trigger piede con accelerometro"""
    print("=" * 60)
    print("ESEMPIO 2: Trigger Piede (Accelerometro)")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Test con diversi valori di accelerazione
    test_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    
    for acc in test_values:
        triggered, intensity = trigger_sys.trigger_piede(acc)
        status = "✅ TRIGGER" if triggered else "❌ No trigger"
        print(f"Accelerazione: {acc:.2f} g → {status} (intensità: {intensity:.3f})")
    print()

def esempio_trigger_mano():
    """Esempio: Trigger mano con pose detection"""
    print("=" * 60)
    print("ESEMPIO 3: Trigger Mano (Pose Detection)")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Test con diversi valori di velocità
    test_values = [0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
    
    for vel in test_values:
        triggered, intensity = trigger_sys.trigger_mano(vel)
        compensazione = trigger_sys.compensa_latenza_mano(velocita_mano=vel)
        status = "✅ TRIGGER" if triggered else "❌ No trigger"
        print(f"Velocità: {vel:.2f} → {status} (intensità: {intensity:.3f}, compensazione: {compensazione:.2f} ms)")
    print()

def esempio_trigger_microfono():
    """Esempio: Trigger microfono su superficie"""
    print("=" * 60)
    print("ESEMPIO 4: Trigger Microfono (Superficie)")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Test con diversi valori di ampiezza
    test_values = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.7]
    
    for amp in test_values:
        triggered, intensity = trigger_sys.trigger_microfono(amp)
        picco = trigger_sys.calcola_picco([amp])
        status = "✅ TRIGGER" if triggered else "❌ No trigger"
        print(f"Ampiezza: {amp:.3f} → {status} (intensità: {intensity:.3f}, picco: {picco:.3f})")
    print()

def esempio_volume_dinamico():
    """Esempio: Calcolo volume dinamico"""
    print("=" * 60)
    print("ESEMPIO 5: Modulazione Volume Dinamico")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Test con diverse intensità
    test_intensities = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    for intensity in test_intensities:
        volume = trigger_sys.calcola_volume(intensity)
        print(f"Intensità: {intensity:.2f} → Volume: {volume:.3f}")
    print()

def esempio_mappatura_suoni():
    """Esempio: Mappatura trigger a suoni"""
    print("=" * 60)
    print("ESEMPIO 6: Mappatura Trigger → Suoni")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Test diversi tipi di trigger
    test_cases = [
        ('piede', True, 0.8),
        ('mano', True, 0.6),
        ('microfono', True, 0.7),
        ('piede', False, 0.3),  # Non triggerato
    ]
    
    for trigger_type, triggered, intensity in test_cases:
        suono = trigger_sys.mappa_suono(trigger_type, triggered, intensity)
        if suono:
            print(f"Trigger: {trigger_type}, Intensità: {intensity:.2f}")
            print(f"  → Suono: {suono['sound_name']} ({suono['sound']})")
            print(f"  → Volume: {suono['volume']:.3f}")
        else:
            print(f"Trigger: {trigger_type} → Nessun suono (non triggerato)")
    print()

def esempio_processamento_unificato():
    """Esempio: Processamento unificato di tutti i trigger"""
    print("=" * 60)
    print("ESEMPIO 7: Processamento Unificato")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Simula dati da diverse sorgenti
    risultati = trigger_sys.processa_trigger_unificato(
        acceleration_piede=2.0,      # Colpo forte del piede
        velocita_mano=0.7,            # Movimento veloce mano
        amplitude_microfono=0.15      # Piccolo rumore microfono
    )
    
    print(f"Latenza Totale: {risultati['latenza_totale']} ms")
    print(f"\nTrigger Attivi:")
    
    for trigger_type, data in risultati['triggers'].items():
        status = "✅" if data['triggered'] else "❌"
        print(f"  {status} {trigger_type.upper()}:")
        for key, value in data.items():
            if isinstance(value, float):
                print(f"    - {key}: {value:.3f}")
            else:
                print(f"    - {key}: {value}")
    
    print(f"\nSuoni Generati: {len(risultati['suoni'])}")
    for suono in risultati['suoni']:
        print(f"  - {suono['sound_name']}: volume {suono['volume']:.3f}")
    print()

def esempio_statistiche():
    """Esempio: Statistiche del sistema"""
    print("=" * 60)
    print("ESEMPIO 8: Statistiche Sistema")
    print("=" * 60)
    
    trigger_sys = TriggerSystem()
    
    # Processa alcuni frame per popolare i buffer
    for i in range(5):
        trigger_sys.trigger_piede(1.5 + i * 0.1)
        trigger_sys.trigger_mano(0.4 + i * 0.1)
        trigger_sys.trigger_microfono(0.1 + i * 0.05)
    
    stats = trigger_sys.get_statistics()
    
    print("Statistiche Sistema:")
    print(f"  Latenza Totale: {stats['latenza_totale']} ms")
    print(f"\n  Soglie:")
    for key, value in stats['soglie'].items():
        print(f"    - {key}: {value}")
    print(f"\n  Range Volume: {stats['volume_range']['min']} - {stats['volume_range']['max']}")
    print(f"\n  Buffer Sizes:")
    for key, value in stats['buffer_sizes'].items():
        print(f"    - {key}: {value}")
    print()

def main():
    """Esegue tutti gli esempi"""
    print("\n" + "=" * 60)
    print("📚 ESEMPI TRIGGER SYSTEM")
    print("=" * 60 + "\n")
    
    esempi = [
        esempio_latenza,
        esempio_trigger_piede,
        esempio_trigger_mano,
        esempio_trigger_microfono,
        esempio_volume_dinamico,
        esempio_mappatura_suoni,
        esempio_processamento_unificato,
        esempio_statistiche
    ]
    
    for esempio in esempi:
        try:
            esempio()
            time.sleep(0.5)  # Pausa tra esempi
        except Exception as e:
            print(f"❌ Errore in {esempio.__name__}: {e}\n")
    
    print("=" * 60)
    print("✅ Tutti gli esempi completati!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

