"""
Script di test per verificare i componenti individuali
"""
import sys

def test_motion_tracker():
    """Test del motion tracker"""
    print("Test Motion Tracker...")
    from src.motion_tracker import MotionTracker
    
    tracker = MotionTracker()
    if tracker.initialize_camera():
        print("✓ Videocamera inizializzata correttamente")
        frame = tracker.get_frame()
        if frame is not None:
            print("✓ Frame acquisito correttamente")
            pose = tracker.detect_pose(frame)
            if pose:
                print("✓ Posa rilevata!")
            else:
                print("⚠ Nessuna posa rilevata (normale se non c'è nessuno davanti alla camera)")
        tracker.release()
    else:
        print("✗ Errore: videocamera non disponibile")
    print()

def test_drum_machine():
    """Test della drum machine"""
    print("Test Drum Machine...")
    from src.drum_machine import DrumMachine
    import time
    
    drum = DrumMachine()
    print("✓ Drum Machine inizializzata")
    
    print("Test suoni...")
    sounds = ['kick', 'snare', 'hihat', 'crash', 'tom1', 'tom2']
    for sound in sounds:
        print(f"  Suonando {sound}...")
        drum.play_sound(sound)
        time.sleep(0.3)
    
    print("✓ Tutti i suoni testati")
    print()

def test_virtual_environment():
    """Test dell'ambiente virtuale"""
    print("Test Virtual Environment...")
    from src.virtual_environment import VirtualEnvironment
    import time
    
    env = VirtualEnvironment()
    print("✓ Ambiente virtuale inizializzato")
    
    # Test aggiornamento per 2 secondi
    print("Visualizzazione ambiente (2 secondi)...")
    start_time = time.time()
    while time.time() - start_time < 2:
        if not env.check_events():
            break
        env.update()
        time.sleep(0.016)  # ~60 FPS
    
    env.close()
    print("✓ Ambiente virtuale testato")
    print()

def test_zone_detector():
    """Test del zone detector"""
    print("Test Zone Detector...")
    from src.zone_detector import ZoneDetector
    import numpy as np
    
    detector = ZoneDetector()
    print("✓ Zone Detector inizializzato")
    
    # Test con punti di esempio
    key_points = {
        'left_wrist': np.array([0.5, 0.5, 0.0]),  # Centro snare
        'right_wrist': np.array([0.3, 0.4, 0.0]),  # Hi-hat
    }
    velocities = {
        'left_wrist': 0.5,
        'right_wrist': 0.4
    }
    
    hits = detector.detect_hits(key_points, velocities)
    print(f"✓ Zone rilevate: {hits}")
    print()

def main():
    """Esegue tutti i test"""
    print("=" * 50)
    print("Test Componenti DrumMan")
    print("=" * 50)
    print()
    
    try:
        test_drum_machine()
        test_virtual_environment()
        test_zone_detector()
        
        # Test motion tracker solo se richiesto (richiede camera)
        response = input("Vuoi testare il Motion Tracker? (richiede videocamera) [s/N]: ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            test_motion_tracker()
        
        print("=" * 50)
        print("Tutti i test completati!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\nTest interrotti dall'utente")
    except Exception as e:
        print(f"\n\nERRORE durante i test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

