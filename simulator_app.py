"""
Simulatore App Batteria - Mostra tutti i calcoli di trigger, latenza e modulazione
in tempo reale o simulato
"""
import time
import random
import numpy as np
from src.trigger_system import TriggerSystem

class DrumSimulator:
    """Simulatore completo che mostra tutti i calcoli insieme"""
    
    def __init__(self):
        """Inizializza il simulatore"""
        self.trigger_system = TriggerSystem()
        self.running = False
        self.simulation_mode = 'realtime'  # 'realtime' o 'simulated'
        self.frame_count = 0
        
    def print_header(self):
        """Stampa header del simulatore"""
        print("=" * 80)
        print("🥁 DRUM SIMULATOR - Sistema Unificato Trigger/Latenza/Modulazione")
        print("=" * 80)
        print()
    
    def print_statistics(self):
        """Stampa statistiche del sistema"""
        stats = self.trigger_system.get_statistics()
        print("\n" + "-" * 80)
        print("📊 STATISTICHE SISTEMA")
        print("-" * 80)
        print(f"Latenza Totale: {stats['latenza_totale']:.2f} ms")
        print(f"\nSoglie Trigger:")
        print(f"  - Piede (accelerazione): {stats['soglie']['piede']:.2f} g")
        print(f"  - Mano (velocità): {stats['soglie']['mano']:.2f}")
        print(f"  - Microfono (ampiezza): {stats['soglie']['microfono']:.2f}")
        print(f"\nRange Volume: {stats['volume_range']['min']:.2f} - {stats['volume_range']['max']:.2f}")
        print("-" * 80)
        print()
    
    def simulate_frame(self, frame_num: int) -> Dict:
        """
        Simula un frame con dati casuali ma realistici
        
        Args:
            frame_num: Numero del frame
        
        Returns:
            Risultati del processamento
        """
        # Genera dati simulati realistici
        # Piede: occasionali picchi di accelerazione
        if random.random() < 0.1:  # 10% probabilità di colpo
            acc_piede = random.uniform(1.5, 3.0)
        else:
            acc_piede = random.uniform(0.1, 0.8)
        
        # Mano: movimenti più frequenti
        if random.random() < 0.3:  # 30% probabilità di movimento veloce
            vel_mano = random.uniform(0.5, 1.2)
        else:
            vel_mano = random.uniform(0.1, 0.4)
        
        # Microfono: picchi occasionali
        if random.random() < 0.15:  # 15% probabilità di colpo
            amp_mic = random.uniform(0.2, 0.8)
        else:
            amp_mic = random.uniform(0.01, 0.15)
        
        # Processa tutti i trigger
        risultati = self.trigger_system.processa_trigger_unificato(
            acceleration_piede=acc_piede,
            velocita_mano=vel_mano,
            amplitude_microfono=amp_mic
        )
        
        return risultati
    
    def print_frame_results(self, frame_num: int, risultati: Dict):
        """Stampa i risultati di un frame"""
        print(f"\n{'='*80}")
        print(f"FRAME #{frame_num} - Timestamp: {risultati['timestamp']:.3f}")
        print(f"{'='*80}")
        
        # Latenza
        print(f"\n⏱️  LATENZA TOTALE: {risultati['latenza_totale']:.2f} ms")
        print(f"   Componenti:")
        print(f"     - Microfono: {self.trigger_system.latencies['microfono']} ms")
        print(f"     - Piede: {self.trigger_system.latencies['piede']} ms")
        print(f"     - Pose: {self.trigger_system.latencies['pose']} ms")
        print(f"     - Compensativo: {self.trigger_system.latencies['compensativo']} ms")
        print(f"     - Drum Machine: {self.trigger_system.latencies['drum_machine']} ms")
        
        # Trigger
        print(f"\n🎯 TRIGGER:")
        
        if 'piede' in risultati['triggers']:
            trig = risultati['triggers']['piede']
            status = "✅ ATTIVO" if trig['triggered'] else "❌ Inattivo"
            print(f"   Piede: {status}")
            print(f"     - Accelerazione: {trig['acceleration']:.3f} g")
            print(f"     - Intensità: {trig['intensity']:.3f}")
        
        if 'mano' in risultati['triggers']:
            trig = risultati['triggers']['mano']
            status = "✅ ATTIVO" if trig['triggered'] else "❌ Inattivo"
            print(f"   Mano: {status}")
            print(f"     - Velocità: {trig['velocity']:.3f}")
            print(f"     - Intensità: {trig['intensity']:.3f}")
            print(f"     - Compensazione Latenza: {trig['compensazione_latenza']:.2f} ms")
        
        if 'microfono' in risultati['triggers']:
            trig = risultati['triggers']['microfono']
            status = "✅ ATTIVO" if trig['triggered'] else "❌ Inattivo"
            print(f"   Microfono: {status}")
            print(f"     - Ampiezza: {trig['amplitude']:.3f}")
            print(f"     - Picco: {trig['picco']:.3f}")
            print(f"     - Intensità: {trig['intensity']:.3f}")
        
        # Suoni generati
        if risultati['suoni']:
            print(f"\n🔊 SUONI GENERATI ({len(risultati['suoni'])}):")
            for i, suono in enumerate(risultati['suoni'], 1):
                print(f"   {i}. {suono['sound_name'].upper()}")
                print(f"      - File: {suono['sound']}")
                print(f"      - Volume: {suono['volume']:.3f} (intensità: {suono['intensity']:.3f})")
                print(f"      - Tipo Trigger: {suono['trigger_type']}")
        else:
            print(f"\n🔇 Nessun suono generato")
    
    def run_simulation(self, num_frames: int = 10, delay: float = 1.0):
        """
        Esegue una simulazione con N frame
        
        Args:
            num_frames: Numero di frame da simulare
            delay: Ritardo tra frame in secondi
        """
        self.print_header()
        self.print_statistics()
        
        print(f"\n🎬 Avvio simulazione: {num_frames} frame, delay {delay}s")
        print("Premi Ctrl+C per interrompere\n")
        
        try:
            for i in range(num_frames):
                risultati = self.simulate_frame(i)
                self.print_frame_results(i, risultati)
                
                if i < num_frames - 1:
                    time.sleep(delay)
            
            print(f"\n{'='*80}")
            print("✅ Simulazione completata!")
            print(f"{'='*80}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Simulazione interrotta dall'utente\n")
    
    def run_realtime_demo(self, duration: float = 10.0, fps: float = 2.0):
        """
        Esegue una demo in tempo reale
        
        Args:
            duration: Durata in secondi
            fps: Frame per secondo
        """
        self.print_header()
        self.print_statistics()
        
        print(f"\n🎬 Demo tempo reale: {duration}s, {fps} FPS")
        print("Premi Ctrl+C per interrompere\n")
        
        start_time = time.time()
        frame_count = 0
        frame_interval = 1.0 / fps
        
        try:
            while time.time() - start_time < duration:
                frame_start = time.time()
                
                risultati = self.simulate_frame(frame_count)
                self.print_frame_results(frame_count, risultati)
                
                frame_count += 1
                
                # Mantieni FPS costante
                elapsed = time.time() - frame_start
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            print(f"\n{'='*80}")
            print(f"✅ Demo completata! ({frame_count} frame processati)")
            print(f"{'='*80}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Demo interrotta dall'utente")
            print(f"Frame processati: {frame_count}\n")
    
    def interactive_mode(self):
        """Modalità interattiva per testare manualmente"""
        self.print_header()
        self.print_statistics()
        
        print("\n🎮 MODALITÀ INTERATTIVA")
        print("Inserisci valori per testare i trigger")
        print("Premi Enter senza valori per uscire\n")
        
        while True:
            try:
                print("\n" + "-" * 80)
                
                # Input piede
                acc_input = input("Accelerazione piede (g) [Enter per skip]: ").strip()
                acc_piede = float(acc_input) if acc_input else None
                
                # Input mano
                vel_input = input("Velocità mano [Enter per skip]: ").strip()
                vel_mano = float(vel_input) if vel_input else None
                
                # Input microfono
                amp_input = input("Ampiezza microfono (0-1) [Enter per skip]: ").strip()
                amp_mic = float(amp_input) if amp_input else None
                
                if acc_piede is None and vel_mano is None and amp_mic is None:
                    print("\n✅ Uscita dalla modalità interattiva\n")
                    break
                
                # Processa
                risultati = self.trigger_system.processa_trigger_unificato(
                    acceleration_piede=acc_piede,
                    velocita_mano=vel_mano,
                    amplitude_microfono=amp_mic
                )
                
                self.print_frame_results(0, risultati)
                
            except ValueError:
                print("⚠️  Valore non valido, riprova")
            except KeyboardInterrupt:
                print("\n\n✅ Uscita dalla modalità interattiva\n")
                break

def main():
    """Funzione principale"""
    simulator = DrumSimulator()
    
    print("\n" + "=" * 80)
    print("🥁 DRUM SIMULATOR - Menu Principale")
    print("=" * 80)
    print("\nScegli modalità:")
    print("1. Simulazione (10 frame, 1s delay)")
    print("2. Demo tempo reale (10s, 2 FPS)")
    print("3. Modalità interattiva (input manuale)")
    print("4. Esci")
    print()
    
    try:
        scelta = input("Scelta [1-4]: ").strip()
        
        if scelta == '1':
            simulator.run_simulation(num_frames=10, delay=1.0)
        elif scelta == '2':
            simulator.run_realtime_demo(duration=10.0, fps=2.0)
        elif scelta == '3':
            simulator.interactive_mode()
        elif scelta == '4':
            print("\n👋 Arrivederci!\n")
        else:
            print("\n⚠️  Scelta non valida\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 Arrivederci!\n")
    except Exception as e:
        print(f"\n\n❌ Errore: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

