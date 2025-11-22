"""
DrumMan - Virtual Drum Machine con Motion Tracking
Entry point principale dell'applicazione - Versione Completa
"""
import sys
import time
import pygame
import numpy as np
from src.motion_tracker import MotionTracker
from src.drum_machine import DrumMachine
from src.virtual_environment import VirtualEnvironment
from src.zone_detector import ZoneDetector
from src.calibration import CalibrationSystem
from src.ui_menu import UIMenu
from src.config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT
)

def main():
    """Funzione principale"""
    print("=" * 60)
    print("DrumMan - Virtual Drum Machine")
    print("Versione Completa con Funzionalità Avanzate")
    print("=" * 60)
    print("\nInizializzazione...")
    
    # Inizializza i componenti
    motion_tracker = MotionTracker(
        camera_index=CAMERA_INDEX,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT
    )
    
    drum_machine = DrumMachine()
    virtual_env = VirtualEnvironment(
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT
    )
    zone_detector = ZoneDetector()
    calibration_system = CalibrationSystem(motion_tracker)
    ui_menu = UIMenu(virtual_env.screen)
    
    # Configura callback per il menu
    ui_menu.register_callback('toggle_metronome', lambda enabled: 
        drum_machine.set_metronome(enabled, ui_menu.settings['metronome_bpm']))
    ui_menu.register_callback('set_metronome_bpm', lambda bpm: 
        drum_machine.set_metronome(ui_menu.settings['metronome_enabled'], bpm))
    ui_menu.register_callback('set_master_volume', lambda vol: 
        drum_machine.set_master_volume(vol))
    ui_menu.register_callback('start_calibration', lambda: 
        calibration_system.calibrate())
    
    # Inizializza la videocamera
    print("Inizializzazione videocamera...")
    if not motion_tracker.initialize_camera():
        print("ERRORE: Impossibile aprire la videocamera!")
        print("Assicurati che la videocamera sia collegata e non utilizzata da altre applicazioni.")
        return
    
    print("✓ Videocamera inizializzata")
    print("✓ Drum Machine pronta")
    print("✓ Ambiente virtuale pronto")
    print("✓ Sistema di calibrazione pronto")
    print("✓ Menu UI pronto")
    
    print("\n" + "=" * 60)
    print("CONTROLLI:")
    print("  TAB     - Apri/Chiudi Menu")
    print("  ESC     - Esci dall'applicazione")
    print("  C       - Calibrazione (nel menu)")
    print("  M       - Metronomo (nel menu)")
    print("  V       - Volume (nel menu)")
    print("=" * 60)
    print("\nAvvio applicazione...\n")
    
    # Loop principale
    running = True
    frame_count = 0
    last_fps_time = time.time()
    current_fps = 0.0
    calibration_requested = False
    
    # Stato per migliorare il tracking
    use_calibration = False
    
    try:
        while running:
            # Controlla eventi
            continue_running, key_pressed = virtual_env.check_events()
            if not continue_running:
                break
            
            # Gestisci input tastiera
            if key_pressed is not None:
                if key_pressed == pygame.K_TAB:
                    ui_menu.toggle_menu()
                elif not ui_menu.is_active():
                    # Solo se il menu non è attivo
                    pass
                else:
                    # Gestisci input nel menu
                    ui_menu.handle_key(key_pressed)
            
            # Aggiorna metronomo
            drum_machine.update_metronome()
            
            # Ottieni frame dalla videocamera
            frame = motion_tracker.get_frame()
            if frame is None:
                continue
            
            # Rileva la posa
            pose_data = motion_tracker.detect_pose(frame)
            
            active_zones = set()
            
            if pose_data is not None:
                key_points = pose_data['key_points']
                
                # Applica calibrazione se disponibile
                if use_calibration and calibration_system.calibration_complete:
                    normalized_key_points = {}
                    for point_name, point_3d in key_points.items():
                        point_type = 'wrist' if 'wrist' in point_name else ('ankle' if 'ankle' in point_name else 'nose')
                        normalized_key_points[point_name] = calibration_system.normalize_position(
                            point_3d, point_type
                        )
                    key_points = normalized_key_points
                
                # Calcola velocità per tutte le articolazioni
                velocities = motion_tracker.get_hand_velocities(key_points)
                
                # Aggiungi velocità per caviglie (per il kick)
                if 'left_ankle' in key_points:
                    current_time = time.time()
                    dt = current_time - motion_tracker.last_time
                    if 'left_ankle' in motion_tracker.last_positions:
                        velocities['left_ankle'] = motion_tracker.calculate_velocity(
                            key_points['left_ankle'],
                            motion_tracker.last_positions['left_ankle'],
                            dt
                        )
                        motion_tracker.last_positions['left_ankle'] = key_points['left_ankle']
                    else:
                        velocities['left_ankle'] = 0.0
                        motion_tracker.last_positions['left_ankle'] = key_points['left_ankle']
                
                if 'right_ankle' in key_points:
                    current_time = time.time()
                    dt = current_time - motion_tracker.last_time
                    if 'right_ankle' in motion_tracker.last_positions:
                        velocities['right_ankle'] = motion_tracker.calculate_velocity(
                            key_points['right_ankle'],
                            motion_tracker.last_positions['right_ankle'],
                            dt
                        )
                        motion_tracker.last_positions['right_ankle'] = key_points['right_ankle']
                    else:
                        velocities['right_ankle'] = 0.0
                        motion_tracker.last_positions['right_ankle'] = key_points['right_ankle']
                
                # Rileva i colpi
                hit_zones = zone_detector.detect_hits(key_points, velocities)
                
                # Suona i suoni per le zone colpite
                for zone_name in hit_zones:
                    # Calcola la velocità relativa per l'intensità
                    velocity = 1.0
                    
                    # Trova quale articolazione ha colpito
                    if zone_name == 'kick':
                        # Per il kick, usa la velocità della caviglia
                        for foot in ['left_ankle', 'right_ankle']:
                            if foot in key_points:
                                velocity = zone_detector.get_zone_velocity(
                                    key_points[foot],
                                    zone_detector.drum_zones.get(zone_name, {})
                                )
                                # Combina con velocità di movimento
                                velocity = max(velocity, velocities.get(foot, 0) * 0.5)
                                break
                    else:
                        # Per gli altri, usa la velocità del polso
                        for hand in ['left_wrist', 'right_wrist']:
                            if hand in key_points:
                                dist = zone_detector.distance_to_zone(
                                    key_points[hand],
                                    zone_detector.drum_zones.get(zone_name, {}).get('center', np.array([0.5, 0.5, 0]))
                                )
                                if dist <= zone_detector.drum_zones.get(zone_name, {}).get('trigger_distance', 0.2):
                                    velocity = zone_detector.get_zone_velocity(
                                        key_points[hand],
                                        zone_detector.drum_zones.get(zone_name, {})
                                    )
                                    # Combina con velocità di movimento
                                    velocity = max(velocity, velocities.get(hand, 0) * 0.3)
                                    break
                    
                    # Normalizza la velocità
                    velocity = min(1.0, max(0.3, velocity))
                    
                    drum_machine.play_sound(zone_name, velocity)
                    active_zones.add(zone_name)
                
                # Aggiorna l'ambiente virtuale
                virtual_env.update(
                    key_points=key_points, 
                    active_zones=active_zones,
                    fps=current_fps,
                    show_info=not ui_menu.is_active()
                )
            else:
                # Nessuna posa rilevata, mostra solo l'ambiente
                virtual_env.update(fps=current_fps, show_info=not ui_menu.is_active())
            
            # Disegna il menu se attivo
            if ui_menu.is_active():
                ui_menu.draw()
            
            # Calcola FPS (ogni secondo)
            frame_count += 1
            current_time = time.time()
            if current_time - last_fps_time >= 1.0:
                current_fps = frame_count / (current_time - last_fps_time)
                if not ui_menu.is_active():
                    print(f"FPS: {current_fps:.1f} | Zone attive: {len(active_zones)}", end='\r')
                frame_count = 0
                last_fps_time = current_time
    
    except KeyboardInterrupt:
        print("\n\nInterruzione da tastiera...")
    except Exception as e:
        print(f"\n\nERRORE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\nChiusura applicazione...")
        motion_tracker.release()
        drum_machine.stop_all()
        virtual_env.close()
        print("Applicazione chiusa. Arrivederci!")

if __name__ == "__main__":
    main()
