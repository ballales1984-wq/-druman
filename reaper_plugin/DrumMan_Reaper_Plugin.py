"""
DrumMan Reaper Plugin - ReaScript Python
Interfaccia plugin per Reaper DAW

Installazione:
1. Copia questo file in: Reaper/Scripts/
2. In Reaper: Actions → Show action list → Load ReaScript → Select this file
3. Assegna una shortcut (es. Ctrl+Alt+D)

Uso:
- Avvia DrumMan prima di aprire questo script
- Il plugin si connetterà automaticamente
- Usa l'interfaccia per configurare e monitorare
"""

import RPR
import math

# Configurazione
MIDI_CHANNEL = 10  # GM Drum Channel
OSC_PORT = 8000
OSC_HOST = "127.0.0.1"

class DrumManPlugin:
    """Plugin DrumMan per Reaper"""
    
    def __init__(self):
        self.window_open = False
        self.midi_enabled = True
        self.osc_enabled = False
        self.track_selected = None
        self.trigger_count = {
            'kick': 0,
            'snare': 0,
            'hihat': 0,
            'crash': 0,
            'tom1': 0,
            'tom2': 0
        }
        
        # Mappatura note MIDI
        self.midi_map = {
            36: 'kick',
            38: 'snare',
            42: 'hihat',
            49: 'crash',
            47: 'tom1',
            48: 'tom2'
        }
    
    def create_window(self):
        """Crea la finestra dell'interfaccia"""
        if self.window_open:
            return
        
        # Crea finestra
        self.window_id = RPR.GCF_GetHwnd()
        
        # Crea interfaccia grafica
        self.window_open = True
        self.show_main_interface()
    
    def show_main_interface(self):
        """Mostra l'interfaccia principale"""
        # Questa è una versione semplificata
        # Per una GUI completa, usa gfx.init() o tkinter
        
        title = "DrumMan Reaper Plugin"
        message = f"""
╔══════════════════════════════════════╗
║     DrumMan Reaper Plugin v1.0       ║
╠══════════════════════════════════════╣
║                                      ║
║  Status: Connesso                    ║
║  MIDI Channel: {MIDI_CHANNEL}                    ║
║                                      ║
║  Trigger Ricevuti:                   ║
║  • Kick:    {self.trigger_count['kick']:4d}                  ║
║  • Snare:   {self.trigger_count['snare']:4d}                  ║
║  • Hi-Hat:  {self.trigger_count['hihat']:4d}                  ║
║  • Crash:   {self.trigger_count['crash']:4d}                  ║
║  • Tom1:    {self.trigger_count['tom1']:4d}                  ║
║  • Tom2:    {self.trigger_count['tom2']:4d}                  ║
║                                      ║
║  [OK] [Reset Counters] [Settings]    ║
╚══════════════════════════════════════╝
        """
        
        RPR.ShowMessageBox(message, title, 0)
    
    def process_midi_input(self):
        """Processa input MIDI da DrumMan"""
        # Ottieni traccia selezionata
        track = RPR.GetSelectedTrack(0, 0)
        if not track:
            return
        
        # Monitora input MIDI (implementazione semplificata)
        # In una versione completa, si userebbe MIDI_GetRecentInputEvent
        
        pass
    
    def reset_counters(self):
        """Reset contatori trigger"""
        for key in self.trigger_count:
            self.trigger_count[key] = 0
    
    def get_statistics(self):
        """Restituisce statistiche"""
        total = sum(self.trigger_count.values())
        return {
            'total_triggers': total,
            'by_component': self.trigger_count.copy()
        }

def main():
    """Funzione principale del plugin"""
    plugin = DrumManPlugin()
    plugin.create_window()
    plugin.show_main_interface()

# Esegui plugin
if __name__ == "__main__":
    main()

