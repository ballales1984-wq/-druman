"""
DrumMan Standalone GUI Plugin
Interfaccia grafica standalone che funziona come plugin per Reaper
Può essere usata insieme a Reaper o standalone
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Dict, Optional

try:
    from src.reaper_connector import ReaperConnector, ConnectionType
    REAPER_AVAILABLE = True
except ImportError:
    REAPER_AVAILABLE = False
    print("⚠️  Reaper connector non disponibile")

class DrumManPluginGUI:
    """Interfaccia grafica plugin-like per DrumMan"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DrumMan - Reaper Plugin Interface")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Connettore Reaper
        self.reaper_connector = None
        self.connected = False
        
        # Statistiche
        self.stats = {
            'kick': 0,
            'snare': 0,
            'hihat': 0,
            'crash': 0,
            'tom1': 0,
            'tom2': 0,
            'total': 0
        }
        
        # Variabili
        self.connection_type = tk.StringVar(value="midi")
        self.midi_port = tk.StringVar(value="")
        self.osc_host = tk.StringVar(value="127.0.0.1")
        self.osc_port = tk.IntVar(value=8000)
        
        # Crea interfaccia
        self.create_widgets()
        
        # Thread per aggiornamento
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
    def create_widgets(self):
        """Crea i widget dell'interfaccia"""
        
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titolo
        title_label = ttk.Label(main_frame, text="🥁 DrumMan Reaper Plugin", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Sezione connessione
        conn_frame = ttk.LabelFrame(main_frame, text="Connessione", padding="10")
        conn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Tipo connessione
        ttk.Label(conn_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=5)
        conn_type_combo = ttk.Combobox(conn_frame, textvariable=self.connection_type,
                                       values=["midi", "osc", "both"], state="readonly", width=15)
        conn_type_combo.grid(row=0, column=1, padx=5)
        
        # MIDI Port
        ttk.Label(conn_frame, text="MIDI Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        midi_port_combo = ttk.Combobox(conn_frame, textvariable=self.midi_port, width=30)
        midi_port_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # OSC Host
        ttk.Label(conn_frame, text="OSC Host:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(conn_frame, textvariable=self.osc_host, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # OSC Port
        ttk.Label(conn_frame, text="OSC Port:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(conn_frame, textvariable=self.osc_port, width=30).grid(row=3, column=1, padx=5, pady=5)
        
        # Pulsanti connessione
        button_frame = ttk.Frame(conn_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.connect_btn = ttk.Button(button_frame, text="Connetti", command=self.connect_reaper)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = ttk.Button(button_frame, text="Disconnetti", 
                                         command=self.disconnect_reaper, state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(button_frame, text="Aggiorna Porte MIDI", 
                                      command=self.refresh_midi_ports)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(conn_frame, text="Status: Disconnesso", 
                                     foreground="red", font=("Arial", 10, "bold"))
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # Sezione statistiche
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiche Trigger", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Griglia statistiche
        self.stats_labels = {}
        components = ['kick', 'snare', 'hihat', 'crash', 'tom1', 'tom2']
        
        for i, comp in enumerate(components):
            ttk.Label(stats_frame, text=f"{comp.upper()}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            label = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
            label.grid(row=i, column=1, sticky=tk.W, padx=10, pady=2)
            self.stats_labels[comp] = label
        
        # Totale
        ttk.Label(stats_frame, text="TOTALE:", font=("Arial", 10, "bold")).grid(
            row=len(components), column=0, sticky=tk.W, padx=5, pady=5)
        self.total_label = ttk.Label(stats_frame, text="0", font=("Arial", 12, "bold"), 
                                    foreground="blue")
        self.total_label.grid(row=len(components), column=1, sticky=tk.W, padx=10, pady=5)
        
        # Pulsante reset
        ttk.Button(stats_frame, text="Reset Contatori", command=self.reset_stats).grid(
            row=len(components)+1, column=0, columnspan=2, pady=10)
        
        # Sezione informazioni
        info_frame = ttk.LabelFrame(main_frame, text="Informazioni", padding="10")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        info_text = """
DrumMan invia trigger MIDI/OSC a Reaper quando rileva movimenti.
Assicurati che:
• Reaper sia aperto e configurato per ricevere MIDI
• Una traccia MIDI sia impostata sul canale 10 (GM Drum)
• Un VST drum machine sia caricato sulla traccia
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Configura griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def refresh_midi_ports(self):
        """Aggiorna lista porte MIDI"""
        if REAPER_AVAILABLE:
            try:
                connector = ReaperConnector(connection_type=ConnectionType.MIDI)
                ports = connector.get_available_midi_ports()
                # Aggiorna combobox (implementazione semplificata)
                print(f"Porte MIDI disponibili: {ports}")
                messagebox.showinfo("Porte MIDI", f"Porte disponibili:\n" + "\n".join(ports))
            except Exception as e:
                messagebox.showerror("Errore", f"Errore aggiornamento porte: {e}")
    
    def connect_reaper(self):
        """Connetti a Reaper"""
        if not REAPER_AVAILABLE:
            messagebox.showerror("Errore", "Reaper connector non disponibile!")
            return
        
        try:
            # Determina tipo connessione
            conn_type_map = {
                'midi': ConnectionType.MIDI,
                'osc': ConnectionType.OSC,
                'both': ConnectionType.BOTH
            }
            conn_type = conn_type_map.get(self.connection_type.get(), ConnectionType.MIDI)
            
            # Crea connettore
            midi_port = self.midi_port.get() if self.midi_port.get() else None
            self.reaper_connector = ReaperConnector(
                connection_type=conn_type,
                midi_port=midi_port,
                osc_host=self.osc_host.get(),
                osc_port=self.osc_port.get()
            )
            
            # Abilita
            if self.reaper_connector.enable():
                self.connected = True
                self.status_label.config(text="Status: Connesso", foreground="green")
                self.connect_btn.config(state=tk.DISABLED)
                self.disconnect_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Successo", "Connesso a Reaper!")
            else:
                messagebox.showerror("Errore", "Impossibile connettersi a Reaper!")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore connessione: {e}")
    
    def disconnect_reaper(self):
        """Disconnetti da Reaper"""
        if self.reaper_connector:
            self.reaper_connector.close()
            self.reaper_connector = None
        
        self.connected = False
        self.status_label.config(text="Status: Disconnesso", foreground="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
    
    def reset_stats(self):
        """Reset statistiche"""
        for key in self.stats:
            self.stats[key] = 0
        self.update_stats_display()
    
    def update_stats_display(self):
        """Aggiorna display statistiche"""
        if self.reaper_connector:
            connector_stats = self.reaper_connector.get_statistics()
            stats = connector_stats.get('stats', {})
            
            # Aggiorna contatori per componente
            trigger_count = stats.get('trigger_count', {})
            for comp, label in self.stats_labels.items():
                count = trigger_count.get(comp, 0)
                label.config(text=str(count))
                self.stats[comp] = count
            
            # Totale
            total = sum(trigger_count.values())
            self.stats['total'] = total
            self.total_label.config(text=str(total))
    
    def update_loop(self):
        """Loop di aggiornamento"""
        while self.running:
            if self.connected:
                self.update_stats_display()
            time.sleep(0.5)  # Aggiorna ogni 500ms
    
    def on_closing(self):
        """Chiamato alla chiusura"""
        self.running = False
        if self.reaper_connector:
            self.disconnect_reaper()
        self.root.destroy()

def main():
    """Avvia l'interfaccia plugin"""
    root = tk.Tk()
    app = DrumManPluginGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

