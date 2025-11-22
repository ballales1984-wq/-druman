"""
Interfaccia grafica per la libreria di suoni
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict
import os

try:
    from src.sound_library import SoundLibrary, SoundSample
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False


class SoundLibraryUI:
    """Interfaccia grafica per gestire la libreria di suoni"""
    
    def __init__(self, root, sound_library: SoundLibrary):
        """
        Inizializza l'interfaccia
        
        Args:
            root: Finestra Tkinter principale
            sound_library: Istanza SoundLibrary
        """
        self.root = root
        self.library = sound_library
        self.current_sample: Optional[str] = None
        
        self.root.title("DrumMan - Libreria Suoni")
        self.root.geometry("900x700")
        
        self.create_widgets()
        self.refresh_sample_list()
    
    def create_widgets(self):
        """Crea i widget dell'interfaccia"""
        
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titolo
        title = ttk.Label(main_frame, text="🎵 Libreria Suoni di Batteria", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sezione sinistra: Lista campioni
        left_frame = ttk.LabelFrame(main_frame, text="Campioni", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Lista campioni
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.sample_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=15)
        self.sample_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sample_listbox.bind('<<ListboxSelect>>', self.on_sample_select)
        scrollbar.config(command=self.sample_listbox.yview)
        
        # Pulsanti gestione campioni
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Carica File", command=self.load_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Carica Cartella", command=self.load_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Rimuovi", command=self.remove_sample).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Esporta", command=self.export_sample).pack(side=tk.LEFT, padx=2)
        
        # Sezione centrale: Parametri
        center_frame = ttk.LabelFrame(main_frame, text="Parametri Modifica", padding="10")
        center_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        self.param_widgets = {}
        self.create_parameter_widgets(center_frame)
        
        # Sezione destra: Preset
        right_frame = ttk.LabelFrame(main_frame, text="Preset", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Lista preset
        preset_list_frame = ttk.Frame(right_frame)
        preset_list_frame.pack(fill=tk.BOTH, expand=True)
        
        preset_scrollbar = ttk.Scrollbar(preset_list_frame)
        preset_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preset_listbox = tk.Listbox(preset_list_frame, yscrollcommand=preset_scrollbar.set, height=10)
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preset_scrollbar.config(command=self.preset_listbox.yview)
        
        # Pulsanti preset
        preset_btn_frame = ttk.Frame(right_frame)
        preset_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(preset_btn_frame, text="Salva Preset", command=self.save_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_btn_frame, text="Carica Preset", command=self.load_preset).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_btn_frame, text="Elimina Preset", command=self.delete_preset).pack(side=tk.LEFT, padx=2)
        
        # Entry nome preset
        preset_name_frame = ttk.Frame(right_frame)
        preset_name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(preset_name_frame, text="Nome:").pack(side=tk.LEFT, padx=5)
        self.preset_name_entry = ttk.Entry(preset_name_frame, width=20)
        self.preset_name_entry.pack(side=tk.LEFT, padx=5)
        
        # Info campione
        info_frame = ttk.LabelFrame(main_frame, text="Informazioni", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.info_label = ttk.Label(info_frame, text="Seleziona un campione per vedere le informazioni", 
                                   justify=tk.LEFT)
        self.info_label.pack(anchor=tk.W)
        
        # Configura griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def create_parameter_widgets(self, parent):
        """Crea widget per i parametri"""
        
        params = [
            ('volume', 'Volume', 0.0, 2.0),
            ('pitch', 'Pitch', 0.5, 2.0),
            ('speed', 'Velocità', 0.5, 2.0),
            ('attack', 'Attack', 0.0, 1.0),
            ('decay', 'Decay', 0.0, 1.0),
            ('sustain', 'Sustain', 0.0, 1.0),
            ('release', 'Release', 0.0, 1.0),
            ('lowpass_freq', 'Lowpass (Hz)', 20, 20000),
            ('highpass_freq', 'Highpass (Hz)', 0, 20000),
            ('reverb', 'Riverbero', 0.0, 1.0),
            ('distortion', 'Distorsione', 0.0, 1.0),
            ('pan', 'Panoramica', -1.0, 1.0),
        ]
        
        row = 0
        for param_name, label, min_val, max_val in params:
            # Label
            ttk.Label(parent, text=label + ":").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Scale
            var = tk.DoubleVar()
            scale = ttk.Scale(parent, from_=min_val, to=max_val, variable=var, 
                            orient=tk.HORIZONTAL, length=200,
                            command=lambda v, p=param_name: self.on_parameter_change(p, float(v)))
            scale.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
            
            # Value label
            value_label = ttk.Label(parent, text="0.0", width=8)
            value_label.grid(row=row, column=2, padx=5, pady=2)
            
            # Reset button
            reset_btn = ttk.Button(parent, text="Reset", width=8,
                                  command=lambda p=param_name: self.reset_parameter(p))
            reset_btn.grid(row=row, column=3, padx=2, pady=2)
            
            self.param_widgets[param_name] = {
                'var': var,
                'scale': scale,
                'label': value_label,
                'reset': reset_btn
            }
            
            row += 1
        
        # Pulsante reset tutti
        ttk.Button(parent, text="Reset Tutti i Parametri", 
                  command=self.reset_all_parameters).grid(row=row, column=0, columnspan=4, pady=10)
        
        parent.columnconfigure(1, weight=1)
    
    def refresh_sample_list(self):
        """Aggiorna lista campioni"""
        self.sample_listbox.delete(0, tk.END)
        for sample_name in self.library.list_samples():
            self.sample_listbox.insert(tk.END, sample_name)
    
    def refresh_preset_list(self):
        """Aggiorna lista preset"""
        self.preset_listbox.delete(0, tk.END)
        for preset_name in self.library.list_presets():
            self.preset_listbox.insert(tk.END, preset_name)
    
    def on_sample_select(self, event):
        """Chiamato quando si seleziona un campione"""
        selection = self.sample_listbox.curselection()
        if not selection:
            return
        
        sample_name = self.sample_listbox.get(selection[0])
        self.current_sample = sample_name
        
        sample = self.library.get_sample(sample_name)
        if sample:
            # Aggiorna parametri
            for param_name, widgets in self.param_widgets.items():
                value = sample.get_parameter(param_name)
                widgets['var'].set(value)
                widgets['label'].config(text=f"{value:.2f}")
            
            # Aggiorna info
            info = f"""
Nome: {sample.name}
File: {sample.file_path or 'N/A'}
Durata: {sample.metadata['duration']:.2f}s
Sample Rate: {sample.sample_rate} Hz
Canali: {sample.metadata['channels']}
            """
            self.info_label.config(text=info.strip())
    
    def on_parameter_change(self, param_name: str, value: float):
        """Chiamato quando cambia un parametro"""
        if not self.current_sample:
            return
        
        sample = self.library.get_sample(self.current_sample)
        if sample:
            sample.set_parameter(param_name, value)
            self.param_widgets[param_name]['label'].config(text=f"{value:.2f}")
    
    def reset_parameter(self, param_name: str):
        """Reset un parametro"""
        if not self.current_sample:
            return
        
        sample = self.library.get_sample(self.current_sample)
        if sample:
            default_values = {
                'volume': 1.0, 'pitch': 1.0, 'speed': 1.0,
                'attack': 0.0, 'decay': 1.0, 'sustain': 1.0, 'release': 0.0,
                'lowpass_freq': 20000, 'highpass_freq': 0,
                'reverb': 0.0, 'distortion': 0.0, 'pan': 0.0
            }
            default = default_values.get(param_name, 0.0)
            sample.set_parameter(param_name, default)
            self.param_widgets[param_name]['var'].set(default)
            self.param_widgets[param_name]['label'].config(text=f"{default:.2f}")
    
    def reset_all_parameters(self):
        """Reset tutti i parametri"""
        if not self.current_sample:
            return
        
        sample = self.library.get_sample(self.current_sample)
        if sample:
            sample.reset_parameters()
            self.on_sample_select(None)  # Refresh display
    
    def load_file(self):
        """Carica un file audio"""
        file_path = filedialog.askopenfilename(
            title="Carica File Audio",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.ogg *.aiff"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            name = os.path.splitext(os.path.basename(file_path))[0]
            drum_name = tk.simpledialog.askstring("Nome Campione", 
                                                 f"Inserisci nome componente (kick, snare, etc.):\nFile: {name}",
                                                 initialvalue=name.lower())
            
            if drum_name:
                if self.library.load_sample_from_file(drum_name, file_path):
                    messagebox.showinfo("Successo", f"Campione {drum_name} caricato!")
                    self.refresh_sample_list()
                else:
                    messagebox.showerror("Errore", "Errore nel caricamento del file")
    
    def load_folder(self):
        """Carica campioni da una cartella"""
        folder_path = filedialog.askdirectory(title="Seleziona Cartella con File Audio")
        
        if folder_path:
            self.library.import_samples_from_folder(folder_path)
            messagebox.showinfo("Successo", "Campioni caricati dalla cartella!")
            self.refresh_sample_list()
    
    def remove_sample(self):
        """Rimuove un campione"""
        selection = self.sample_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un campione da rimuovere")
            return
        
        sample_name = self.sample_listbox.get(selection[0])
        if messagebox.askyesno("Conferma", f"Rimuovere il campione '{sample_name}'?"):
            if self.library.remove_sample(sample_name):
                messagebox.showinfo("Successo", f"Campione {sample_name} rimosso!")
                self.refresh_sample_list()
                self.current_sample = None
    
    def export_sample(self):
        """Esporta un campione modificato"""
        if not self.current_sample:
            messagebox.showwarning("Attenzione", "Seleziona un campione da esportare")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Esporta Campione",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.library.export_sample(self.current_sample, file_path):
                messagebox.showinfo("Successo", f"Campione esportato: {file_path}")
            else:
                messagebox.showerror("Errore", "Errore nell'esportazione")
    
    def save_preset(self):
        """Salva un preset"""
        preset_name = self.preset_name_entry.get().strip()
        if not preset_name:
            messagebox.showwarning("Attenzione", "Inserisci un nome per il preset")
            return
        
        self.library.save_preset(preset_name)
        messagebox.showinfo("Successo", f"Preset '{preset_name}' salvato!")
        self.refresh_preset_list()
        self.preset_name_entry.delete(0, tk.END)
    
    def load_preset(self):
        """Carica un preset"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un preset da caricare")
            return
        
        preset_name = self.preset_listbox.get(selection[0])
        if self.library.load_preset(preset_name):
            messagebox.showinfo("Successo", f"Preset '{preset_name}' caricato!")
            if self.current_sample:
                self.on_sample_select(None)  # Refresh
        else:
            messagebox.showerror("Errore", "Errore nel caricamento del preset")
    
    def delete_preset(self):
        """Elimina un preset"""
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un preset da eliminare")
            return
        
        preset_name = self.preset_listbox.get(selection[0])
        if messagebox.askyesno("Conferma", f"Eliminare il preset '{preset_name}'?"):
            if self.library.delete_preset(preset_name):
                messagebox.showinfo("Successo", f"Preset {preset_name} eliminato!")
                self.refresh_preset_list()


def main():
    """Avvia l'interfaccia libreria"""
    if not LIBRARY_AVAILABLE:
        print("❌ SoundLibrary non disponibile!")
        return
    
    from src.sound_library import SoundLibrary
    
    root = tk.Tk()
    library = SoundLibrary()
    app = SoundLibraryUI(root, library)
    
    # Refresh preset list
    app.refresh_preset_list()
    
    root.mainloop()


if __name__ == "__main__":
    import tkinter.simpledialog
    main()

