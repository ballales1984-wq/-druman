"""
DrumMan - Virtual Drum Machine con Motion Tracking
Entry point principale dell'applicazione - Versione Completa

Copyright (c) 2024 Alessio Ballini
Email: ballales1984@gmail.com
"""
import sys
import time
import pygame
import numpy as np
from src.motion_tracker import MotionTracker
from src.drum_machine import DrumMachine
from src.virtual_environment import VirtualEnvironment
from src.video_overlay import VideoOverlay
from src.beatbox_detector import BeatboxDetector
from src.height_detector import HeightDetector
from src.pad_calibrator import PadCalibrator
from src.zone_detector import ZoneDetector
from src.calibration import CalibrationSystem
from src.ui_menu import UIMenu
from src.reaper_connector import ReaperConnector, ConnectionType
from src.config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    REAPER_ENABLED, REAPER_CONNECTION_TYPE, REAPER_MIDI_PORT,
    REAPER_OSC_HOST, REAPER_OSC_PORT,
    USE_SOUND_LIBRARY, SOUND_LIBRARY_PATH,
    USE_VIDEO_OVERLAY, BEATBOX_MODE
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
    
    drum_machine = DrumMachine(
        use_sound_library=USE_SOUND_LIBRARY,
        library_path=SOUND_LIBRARY_PATH
    )
    
    # Inizializza visualizzazione (video overlay o 3D)
    if USE_VIDEO_OVERLAY:
        # Usa video overlay (video live con rettangoli verdi)
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("DrumMan - Video Overlay Mode")
        video_overlay = VideoOverlay(screen, CAMERA_WIDTH, CAMERA_HEIGHT)
        virtual_env = None  # Non usato in modalità video
    else:
        # Usa ambiente 3D tradizionale
        virtual_env = VirtualEnvironment(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT
        )
        video_overlay = None
        screen = virtual_env.screen
    
    zone_detector = ZoneDetector()
    calibration_system = CalibrationSystem(motion_tracker)
    
    # Sistema di rilevamento altezza automatico (DISABILITATO per configurazione batterista seduto)
    height_detector = None  # Non necessario per configurazione sinistra/destra
    auto_calibration_active = False
    
    # Calibratore interattivo per pad
    pad_calibrator = PadCalibrator(screen, CAMERA_WIDTH, CAMERA_HEIGHT)
    
    ui_menu = UIMenu(screen)
    
    # Inizializza Reaper Connector (opzionale) - PRIMA di beatbox
    reaper_connector = None
    if REAPER_ENABLED:
        try:
            connection_type_map = {
                'midi': ConnectionType.MIDI,
                'osc': ConnectionType.OSC,
                'both': ConnectionType.BOTH
            }
            conn_type = connection_type_map.get(REAPER_CONNECTION_TYPE, ConnectionType.MIDI)
            
            reaper_connector = ReaperConnector(
                connection_type=conn_type,
                midi_port=REAPER_MIDI_PORT,
                osc_host=REAPER_OSC_HOST,
                osc_port=REAPER_OSC_PORT
            )
            
            if reaper_connector.enable():
                print("✓ Reaper Connector abilitato")
            else:
                print("⚠️  Reaper Connector non disponibile (verifica MIDI/OSC)")
                reaper_connector = None
        except Exception as e:
            print(f"[WARN] Errore inizializzazione Reaper: {e}")
            reaper_connector = None
    
    # Inizializza beatbox detector se abilitato (DOPO reaper_connector)
    beatbox_detector = None
    if BEATBOX_MODE:
        def beatbox_callback(drum_name, intensity):
            """Callback quando rileva un suono beatbox"""
            drum_machine.play_sound(drum_name, intensity)
            if reaper_connector and reaper_connector.enabled:
                reaper_connector.send_trigger(drum_name, intensity)
            if video_overlay:
                video_overlay.set_active_pad(drum_name, True, intensity)
        
        beatbox_detector = BeatboxDetector(callback=beatbox_callback)
        beatbox_detector.start_recording()
        print("[OK] Modalità Beatbox attivata")
    
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
    
    print("[OK] Videocamera inizializzata")
    print("[OK] Drum Machine pronta")
    if USE_VIDEO_OVERLAY:
        print("[OK] Video Overlay Mode attivo")
    else:
        print("[OK] Ambiente virtuale 3D pronto")
    print("[OK] Sistema di calibrazione pronto")
    print("[OK] Menu UI pronto")
    if reaper_connector and reaper_connector.enabled:
        print("[OK] Reaper Connector attivo")
    if BEATBOX_MODE:
        print("[OK] Modalità Beatbox attiva - Canta i suoni della batteria!")
    
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
            if virtual_env:
                continue_running, key_pressed = virtual_env.check_events()
            else:
                # Gestione eventi per video overlay
                continue_running = True
                key_pressed = None
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        continue_running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        key_pressed = event.key
                        if event.key == pygame.K_ESCAPE:
                            continue_running = False
                            break
            
            if not continue_running:
                break
            
            # Gestisci eventi mouse per calibrazione
            if pad_calibrator.is_calibrating():
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pad_calibrator.handle_mouse_down(event.pos, event.button)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        pad_calibrator.handle_mouse_up()
                    elif event.type == pygame.MOUSEMOTION:
                        pad_calibrator.handle_mouse_motion(event.pos)
            
            # Gestisci input tastiera
            if key_pressed is not None:
                if key_pressed == pygame.K_TAB:
                    ui_menu.toggle_menu()
                elif key_pressed == pygame.K_c:
                    # Tasto C per calibrazione pad
                    if not pad_calibrator.is_calibrating():
                        pad_calibrator.start_calibration()
                        print("[INFO] Modalità calibrazione attivata - Premi C di nuovo per uscire")
                    else:
                        pad_calibrator.stop_calibration()
                elif pad_calibrator.is_calibrating():
                    # Se sta calibrando, gestisci input calibrazione
                    pad_calibrator.handle_key(key_pressed)
                elif not ui_menu.is_active():
                    # Solo se il menu non è attivo
                    pass
                else:
                    # Gestisci input nel menu
                    ui_menu.handle_key(key_pressed)
            
            # Aggiorna metronomo
            drum_machine.update_metronome()
            
            # Ottieni frame dalla videocamera (solo se non in modalità beatbox)
            frame = None
            pose_data = None
            
            if not BEATBOX_MODE:
                frame = motion_tracker.get_frame()
                if frame is None:
                    continue
                
                # Rileva la posa
                pose_data = motion_tracker.detect_pose(frame)
                
                # Calibrazione automatica altezza (DISABILITATA per configurazione batterista seduto)
            elif USE_VIDEO_OVERLAY and video_overlay:
                # In modalità beatbox, mostra solo video senza tracking
                frame = motion_tracker.get_frame()
                if frame is not None:
                    video_overlay.clear()
                    video_overlay.update_frame(frame)
                    video_overlay.draw_all_pads(None, None)
                    stats = beatbox_detector.get_statistics() if beatbox_detector else {}
                    video_overlay.draw_info(current_fps, stats.get('total_detections', 0))
                    pygame.display.flip()
            
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
                
                # Aggiungi velocità per ginocchia (per il kick)
                for knee in ['left_knee', 'right_knee']:
                    if knee in key_points:
                        current_time = time.time()
                        dt = current_time - motion_tracker.last_time
                        if knee in motion_tracker.last_positions:
                            velocities[knee] = motion_tracker.calculate_velocity(
                                key_points[knee],
                                motion_tracker.last_positions[knee],
                                dt
                            )
                            motion_tracker.last_positions[knee] = key_points[knee]
                        else:
                            velocities[knee] = 0.0
                            motion_tracker.last_positions[knee] = key_points[knee]
                
                # Aggiungi anche velocità per caviglie (fallback per kick)
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
                    
                    # Suona localmente
                    drum_machine.play_sound(zone_name, velocity)
                    
                    # Invia a Reaper se abilitato
                    if reaper_connector and reaper_connector.enabled:
                        reaper_connector.send_trigger(zone_name, velocity)
                    
                    active_zones.add(zone_name)
                
                # Aggiorna visualizzazione
                if USE_VIDEO_OVERLAY and video_overlay:
                    # Modalità video overlay
                    video_overlay.clear()
                    video_overlay.update_frame(frame)
                    
                    # Aggiorna pad attivi
                    for zone_name in active_zones:
                        video_overlay.set_active_pad(zone_name, True, 1.0)
                    
                    # Disegna pad (configurazione fissa per batterista seduto)
                    video_overlay.draw_all_pads(key_points, None)
                    
                    # Disegna calibrazione se attiva
                    if pad_calibrator.is_calibrating():
                        pad_calibrator.draw_calibration()
                    
                    video_overlay.draw_info(current_fps, len(active_zones))
                    pygame.display.flip()
                elif virtual_env:
                    # Modalità 3D tradizionale
                    virtual_env.update(
                        key_points=key_points, 
                        active_zones=active_zones,
                        fps=current_fps,
                        show_info=not ui_menu.is_active()
                    )
            else:
                # Nessuna posa rilevata
                if USE_VIDEO_OVERLAY and video_overlay and frame is not None:
                    video_overlay.clear()
                    video_overlay.update_frame(frame)
                    video_overlay.draw_all_pads(None, None)
                    video_overlay.draw_info(current_fps, 0)
                    pygame.display.flip()
                elif virtual_env:
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
        if reaper_connector:
            reaper_connector.close()
        if beatbox_detector:
            beatbox_detector.stop_recording()
        if virtual_env:
            virtual_env.close()
        if video_overlay:
            pygame.quit()
        print("Applicazione chiusa. Arrivederci!")

if __name__ == "__main__":
    main()
