"""
Modulo per collegare DrumMan a Reaper DAW
Supporta MIDI e OSC per inviare trigger a Reaper
"""
import time
from typing import Dict, Optional, List
from enum import Enum

try:
    import mido
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    print("[WARN] mido non installato. Installa con: pip install mido python-rtmidi")

try:
    import pythonosc.udp_client
    OSC_AVAILABLE = True
except ImportError:
    OSC_AVAILABLE = False
    print("[WARN] python-osc non installato. Installa con: pip install python-osc")


class ConnectionType(Enum):
    """Tipo di connessione a Reaper"""
    MIDI = "midi"
    OSC = "osc"
    BOTH = "both"


class ReaperConnector:
    """Classe per connettere DrumMan a Reaper DAW"""
    
    # Mappatura componenti batteria a note MIDI (GM Drum Map)
    DRUM_MIDI_MAP = {
        'kick': 36,      # C2 - Kick Drum
        'snare': 38,     # D2 - Snare Drum
        'hihat': 42,     # F#2 - Hi-Hat Closed
        'crash': 49,     # C#3 - Crash Cymbal
        'tom1': 47,      # B2 - Low-Mid Tom
        'tom2': 48,      # C3 - Hi-Mid Tom
    }
    
    # Mappatura per OSC (percorsi personalizzabili)
    DRUM_OSC_MAP = {
        'kick': '/drum/kick',
        'snare': '/drum/snare',
        'hihat': '/drum/hihat',
        'crash': '/drum/crash',
        'tom1': '/drum/tom1',
        'tom2': '/drum/tom2',
    }
    
    def __init__(self, 
                 connection_type: ConnectionType = ConnectionType.MIDI,
                 midi_port: Optional[str] = None,
                 osc_host: str = '127.0.0.1',
                 osc_port: int = 8000):
        """
        Inizializza il connettore Reaper
        
        Args:
            connection_type: Tipo di connessione (MIDI, OSC, BOTH)
            midi_port: Nome porta MIDI (None = auto-detect)
            osc_host: Host OSC (default: localhost)
            osc_port: Porta OSC (default: 8000)
        """
        self.connection_type = connection_type
        self.osc_host = osc_host
        self.osc_port = osc_port
        
        # MIDI
        self.midi_out = None
        self.midi_available = False
        
        # OSC
        self.osc_client = None
        self.osc_available = False
        
        # Stato
        self.enabled = False
        self.last_sent_times = {}  # Per debounce
        self.debounce_time = 0.01  # 10ms
        
        # Statistiche
        self.stats = {
            'midi_messages_sent': 0,
            'osc_messages_sent': 0,
            'errors': 0,
            'trigger_count': {
                'kick': 0,
                'snare': 0,
                'hihat': 0,
                'crash': 0,
                'tom1': 0,
                'tom2': 0
            }
        }
        
        # Inizializza connessioni
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Inizializza le connessioni MIDI e OSC"""
        
        # Inizializza MIDI
        if self.connection_type in [ConnectionType.MIDI, ConnectionType.BOTH]:
            if MIDI_AVAILABLE:
                try:
                    self._initialize_midi()
                except Exception as e:
                    print(f"[WARN] Errore inizializzazione MIDI: {e}")
            else:
                print("[WARN] MIDI non disponibile (mido non installato)")
        
        # Inizializza OSC
        if self.connection_type in [ConnectionType.OSC, ConnectionType.BOTH]:
            if OSC_AVAILABLE:
                try:
                    self._initialize_osc()
                except Exception as e:
                    print(f"[WARN] Errore inizializzazione OSC: {e}")
            else:
                print("[WARN] OSC non disponibile (python-osc non installato)")
    
    def _initialize_midi(self):
        """Inizializza connessione MIDI"""
        import mido
        
        # Lista porte MIDI disponibili
        output_ports = mido.get_output_names()
        
        if not output_ports:
            print("[WARN] Nessuna porta MIDI disponibile")
            return
        
        print(f"[INFO] Porte MIDI disponibili: {output_ports}")
        
        # Seleziona porta
        if self.midi_port and self.midi_port in output_ports:
            port_name = self.midi_port
        else:
            # Auto-select: cerca "Reaper" o usa la prima disponibile
            port_name = None
            for port in output_ports:
                if 'reaper' in port.lower() or 'loop' in port.lower():
                    port_name = port
                    break
            
            if not port_name:
                port_name = output_ports[0]
        
        try:
            self.midi_out = mido.open_output(port_name)
            self.midi_available = True
            print(f"[OK] MIDI connesso a: {port_name}")
        except Exception as e:
            print(f"[ERROR] Errore apertura porta MIDI {port_name}: {e}")
            self.midi_available = False
    
    def _initialize_osc(self):
        """Inizializza connessione OSC"""
        try:
            self.osc_client = pythonosc.udp_client.SimpleUDPClient(self.osc_host, self.osc_port)
            self.osc_available = True
            print(f"[OK] OSC connesso a: {self.osc_host}:{self.osc_port}")
        except Exception as e:
            print(f"[ERROR] Errore inizializzazione OSC: {e}")
            self.osc_available = False
    
    def enable(self):
        """Abilita l'invio a Reaper"""
        if not self.midi_available and not self.osc_available:
            print("[WARN] Nessuna connessione disponibile (MIDI o OSC)")
            return False
        
        self.enabled = True
        print("[OK] Reaper Connector abilitato")
        return True
    
    def disable(self):
        """Disabilita l'invio a Reaper"""
        self.enabled = False
        print("[PAUSE] Reaper Connector disabilitato")
    
    def send_trigger(self, drum_name: str, velocity: float = 1.0) -> bool:
        """
        Invia un trigger a Reaper
        
        Args:
            drum_name: Nome del componente (kick, snare, etc.)
            velocity: Velocità/intensità (0-1)
        
        Returns:
            True se inviato con successo
        """
        if not self.enabled:
            return False
        
        if drum_name not in self.DRUM_MIDI_MAP:
            return False
        
        # Debounce
        current_time = time.time()
        if drum_name in self.last_sent_times:
            if current_time - self.last_sent_times[drum_name] < self.debounce_time:
                return False
        
        self.last_sent_times[drum_name] = current_time
        
        success = False
        
        # Invia MIDI
        if self.midi_available and self.connection_type in [ConnectionType.MIDI, ConnectionType.BOTH]:
            if self._send_midi(drum_name, velocity):
                success = True
                self.stats['midi_messages_sent'] += 1
                if drum_name in self.stats['trigger_count']:
                    self.stats['trigger_count'][drum_name] += 1
        
        # Invia OSC
        if self.osc_available and self.connection_type in [ConnectionType.OSC, ConnectionType.BOTH]:
            if self._send_osc(drum_name, velocity):
                success = True
                self.stats['osc_messages_sent'] += 1
                if drum_name in self.stats['trigger_count']:
                    self.stats['trigger_count'][drum_name] += 1
        
        return success
    
    def _send_midi(self, drum_name: str, velocity: float) -> bool:
        """Invia messaggio MIDI"""
        try:
            import mido
            
            note = self.DRUM_MIDI_MAP[drum_name]
            velocity_midi = int(velocity * 127)  # Converti 0-1 a 0-127
            
            # Note On
            msg_on = mido.Message('note_on', channel=9, note=note, velocity=velocity_midi)
            self.midi_out.send(msg_on)
            
            # Note Off immediato (per suoni percussivi)
            time.sleep(0.001)  # 1ms
            msg_off = mido.Message('note_off', channel=9, note=note, velocity=0)
            self.midi_out.send(msg_off)
            
            return True
        except Exception as e:
            print(f"[ERROR] Errore invio MIDI: {e}")
            self.stats['errors'] += 1
            return False
    
    def _send_osc(self, drum_name: str, velocity: float) -> bool:
        """Invia messaggio OSC"""
        try:
            path = self.DRUM_OSC_MAP[drum_name]
            self.osc_client.send_message(path, [velocity])
            return True
        except Exception as e:
            print(f"[ERROR] Errore invio OSC: {e}")
            self.stats['errors'] += 1
            return False
    
    def get_available_midi_ports(self) -> List[str]:
        """Restituisce lista porte MIDI disponibili"""
        if not MIDI_AVAILABLE:
            return []
        
        try:
            import mido
            return mido.get_output_names()
        except:
            return []
    
    def set_midi_port(self, port_name: str) -> bool:
        """Cambia porta MIDI"""
        if not MIDI_AVAILABLE:
            return False
        
        try:
            import mido
            if self.midi_out:
                self.midi_out.close()
            
            self.midi_out = mido.open_output(port_name)
            self.midi_available = True
            print(f"[OK] MIDI porta cambiata a: {port_name}")
            return True
        except Exception as e:
            print(f"[ERROR] Errore cambio porta MIDI: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Restituisce statistiche"""
        return {
            'enabled': self.enabled,
            'midi_available': self.midi_available,
            'osc_available': self.osc_available,
            'connection_type': self.connection_type.value,
            'stats': self.stats.copy()
        }
    
    def close(self):
        """Chiude le connessioni"""
        if self.midi_out:
            try:
                self.midi_out.close()
            except:
                pass
        
        self.enabled = False
        print("[OK] Connessioni Reaper chiuse")

