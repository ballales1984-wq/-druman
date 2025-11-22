"""
Sistema unificato per il calcolo di trigger, latenza e modulazione
Integra formule per: mani, piede, microfoni, latenza e compensazioni
"""
import math
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import deque
import time

class TriggerSystem:
    """Sistema completo per gestire trigger da diverse sorgenti"""
    
    def __init__(self):
        """Inizializza il sistema di trigger"""
        # Configurazioni latenza (in ms)
        self.latencies = {
            'microfono': 3,
            'piede': 10,
            'pose': 25,
            'compensativo': 5,
            'drum_machine': 5
        }
        
        # Soglie trigger
        self.thresholds = {
            'piede': 1.5,      # g (accelerazione)
            'mano': 0.5,        # velocità normalizzata
            'microfono': 0.2    # amplitude normalizzata (0-1)
        }
        
        # Volume dinamico
        self.volume_range = {
            'min': 0.2,
            'max': 1.0
        }
        
        # Buffer per smoothing
        self.acceleration_buffer = deque(maxlen=10)
        self.velocity_buffer = deque(maxlen=10)
        self.audio_buffer = deque(maxlen=20)
        
        # Storia trigger per debounce
        self.last_trigger_times = {}
        self.debounce_time = 50  # ms
        
        # Suoni disponibili
        self.available_sounds = {
            'kick': 'kick.wav',
            'snare': 'snare.wav',
            'hihat': 'hi_hat.wav',
            'crash': 'crash.wav',
            'tom1': 'tom1.wav',
            'tom2': 'tom2.wav'
        }
    
    # ===============================
    # 1. LATENZA TOTALE
    # ===============================
    def calcola_latenza_totale(self, 
                               lat_microfono: Optional[float] = None,
                               lat_piede: Optional[float] = None,
                               lat_pose: Optional[float] = None,
                               lat_compensativo: Optional[float] = None,
                               lat_drum_machine: Optional[float] = None) -> float:
        """
        Calcola la latenza totale stimata in ms.
        
        Args:
            lat_microfono: Latenza microfono (ms)
            lat_piede: Latenza piede/accelerometro (ms)
            lat_pose: Latenza pose estimation (ms)
            lat_compensativo: Latenza algoritmo compensativo (ms)
            lat_drum_machine: Latenza drum machine (ms)
        
        Returns:
            Latenza totale in ms
        """
        lat_mic = lat_microfono if lat_microfono is not None else self.latencies['microfono']
        lat_ped = lat_piede if lat_piede is not None else self.latencies['piede']
        lat_pos = lat_pose if lat_pose is not None else self.latencies['pose']
        lat_comp = lat_compensativo if lat_compensativo is not None else self.latencies['compensativo']
        lat_dm = lat_drum_machine if lat_drum_machine is not None else self.latencies['drum_machine']
        
        totale = lat_mic + lat_ped + lat_pos + lat_comp + lat_dm
        return totale
    
    # ===============================
    # 2. TRIGGER COLPO PIEDE (accelerometro)
    # ===============================
    def trigger_piede(self, acceleration: float, soglia: Optional[float] = None) -> Tuple[bool, float]:
        """
        Determina se un colpo del piede ha superato la soglia di accelerazione.
        
        Args:
            acceleration: Accelerazione in g (gravità)
            soglia: Soglia personalizzata (opzionale)
        
        Returns:
            Tuple (triggered, intensity): True se triggerato, intensità (0-1)
        """
        threshold = soglia if soglia is not None else self.thresholds['piede']
        
        # Aggiungi al buffer per smoothing
        self.acceleration_buffer.append(acceleration)
        
        # Calcola media mobile per ridurre falsi positivi
        if len(self.acceleration_buffer) >= 3:
            avg_acc = np.mean(list(self.acceleration_buffer)[-3:])
        else:
            avg_acc = acceleration
        
        triggered = avg_acc >= threshold
        
        # Calcola intensità normalizzata (0-1)
        # Assumiamo che 2.0g sia il massimo tipico
        intensity = min(1.0, max(0.0, (avg_acc - threshold) / (2.0 - threshold)))
        
        return triggered, intensity
    
    # ===============================
    # 3. TRIGGER COLPO MANO (pose detection)
    # ===============================
    def trigger_mano(self, velocita_mano: float, soglia: Optional[float] = None) -> Tuple[bool, float]:
        """
        Determina se il movimento della mano genera un colpo valido.
        
        Args:
            velocita_mano: Velocità in pixel/ms o unità normalizzata
            soglia: Soglia personalizzata (opzionale)
        
        Returns:
            Tuple (triggered, intensity): True se triggerato, intensità (0-1)
        """
        threshold = soglia if soglia is not None else self.thresholds['mano']
        
        # Aggiungi al buffer per smoothing
        self.velocity_buffer.append(velocita_mano)
        
        # Calcola media mobile
        if len(self.velocity_buffer) >= 3:
            avg_vel = np.mean(list(self.velocity_buffer)[-3:])
        else:
            avg_vel = velocita_mano
        
        triggered = avg_vel >= threshold
        
        # Calcola intensità normalizzata
        # Assumiamo che 1.0 sia il massimo tipico
        intensity = min(1.0, max(0.0, (avg_vel - threshold) / (1.0 - threshold)))
        
        return triggered, intensity
    
    # ===============================
    # 4. TRIGGER MICROFONO SU SUPERFICIE
    # ===============================
    def trigger_microfono(self, amplitude: float, soglia: Optional[float] = None) -> Tuple[bool, float]:
        """
        Rileva un colpo su una superficie tramite picco del microfono.
        
        Args:
            amplitude: Valore normalizzato 0-1
            soglia: Soglia personalizzata (opzionale)
        
        Returns:
            Tuple (triggered, intensity): True se triggerato, intensità (0-1)
        """
        threshold = soglia if soglia is not None else self.thresholds['microfono']
        
        # Aggiungi al buffer
        self.audio_buffer.append(amplitude)
        
        # Calcola picco recente
        if len(self.audio_buffer) >= 5:
            recent_peak = max(list(self.audio_buffer)[-5:])
        else:
            recent_peak = amplitude
        
        triggered = recent_peak >= threshold
        
        # Intensità basata sul picco
        intensity = min(1.0, max(0.0, (recent_peak - threshold) / (1.0 - threshold)))
        
        return triggered, intensity
    
    def calcola_picco(self, segnale: List[float]) -> float:
        """
        Calcola picco massimo di un array di segnali audio.
        
        Args:
            segnale: Lista di valori di ampiezza
        
        Returns:
            Picco massimo
        """
        if not segnale:
            return 0.0
        return max(segnale)
    
    # ===============================
    # 5. MODULAZIONE DINAMICA (volume) IN BASE ALL'INTENSITÀ DEL COLPO
    # ===============================
    def calcola_volume(self, intensita: float, min_vol: Optional[float] = None, max_vol: Optional[float] = None) -> float:
        """
        Calcola il volume del colpo in base all'intensità (0-1).
        
        Args:
            intensita: Intensità del colpo (0-1)
            min_vol: Volume minimo (opzionale)
            max_vol: Volume massimo (opzionale)
        
        Returns:
            Volume calcolato (0-1)
        """
        min_v = min_vol if min_vol is not None else self.volume_range['min']
        max_v = max_vol if max_vol is not None else self.volume_range['max']
        
        # Curva non lineare per suono più naturale
        # Usa una curva esponenziale leggera
        intensity_curve = intensita ** 0.7
        
        volume = min_v + (max_v - min_v) * intensity_curve
        return min(max(volume, min_v), max_v)
    
    # ===============================
    # 6. COMPENSAZIONE LATENZA PER MANO
    # ===============================
    def compensa_latenza_mano(self, lat_pose: Optional[float] = None, velocita_mano: float = 0.5) -> float:
        """
        Calcola compensazione del trigger basata su latenza e velocità del movimento.
        
        Args:
            lat_pose: Latenza pose estimation in ms (opzionale)
            velocita_mano: Velocità della mano (normalizzata)
        
        Returns:
            Compensazione in ms
        """
        lat = lat_pose if lat_pose is not None else self.latencies['pose']
        
        # Evita divisione per zero
        if velocita_mano < 0.01:
            velocita_mano = 0.01
        
        # Modello proporzionale: più veloce = meno compensazione necessaria
        compensazione = lat / (velocita_mano * 2)  # Fattore 2 per normalizzazione
        
        return max(0, min(compensazione, lat))  # Limita tra 0 e latenza totale
    
    # ===============================
    # 7. MAPPA COLPO SUONI CAMPIONATI
    # ===============================
    def mappa_suono(self, trigger_type: str, triggered: bool, intensity: float = 1.0) -> Optional[Dict]:
        """
        Assegna un suono dalla lista se il trigger è True.
        
        Args:
            trigger_type: Tipo di trigger ('piede', 'mano', 'microfono')
            triggered: Se il trigger è attivo
            intensity: Intensità del colpo (0-1)
        
        Returns:
            Dizionario con info suono o None
        """
        if not triggered:
            return None
        
        # Mappatura tipo trigger -> suono
        trigger_to_sound = {
            'piede': 'kick',
            'mano': 'snare',  # Default, può essere sovrascritto
            'microfono': 'snare'  # Default
        }
        
        sound_name = trigger_to_sound.get(trigger_type, 'snare')
        
        if sound_name in self.available_sounds:
            # Calcola volume basato su intensità
            volume = self.calcola_volume(intensity)
            
            return {
                'sound': self.available_sounds[sound_name],
                'sound_name': sound_name,
                'volume': volume,
                'intensity': intensity,
                'trigger_type': trigger_type,
                'timestamp': time.time()
            }
        
        return None
    
    # ===============================
    # 8. PROCESSAMENTO UNIFICATO
    # ===============================
    def processa_trigger_unificato(self,
                                   acceleration_piede: Optional[float] = None,
                                   velocita_mano: Optional[float] = None,
                                   amplitude_microfono: Optional[float] = None) -> Dict:
        """
        Processa tutti i trigger insieme e restituisce risultato unificato.
        
        Args:
            acceleration_piede: Accelerazione piede in g
            velocita_mano: Velocità mano normalizzata
            amplitude_microfono: Ampiezza microfono (0-1)
        
        Returns:
            Dizionario con tutti i risultati
        """
        risultati = {
            'latenza_totale': self.calcola_latenza_totale(),
            'triggers': {},
            'suoni': [],
            'timestamp': time.time()
        }
        
        # Processa trigger piede
        if acceleration_piede is not None:
            triggered, intensity = self.trigger_piede(acceleration_piede)
            risultati['triggers']['piede'] = {
                'triggered': triggered,
                'intensity': intensity,
                'acceleration': acceleration_piede
            }
            
            if triggered:
                suono = self.mappa_suono('piede', True, intensity)
                if suono:
                    risultati['suoni'].append(suono)
        
        # Processa trigger mano
        if velocita_mano is not None:
            triggered, intensity = self.trigger_mano(velocita_mano)
            compensazione = self.compensa_latenza_mano(velocita_mano=velocita_mano)
            
            risultati['triggers']['mano'] = {
                'triggered': triggered,
                'intensity': intensity,
                'velocity': velocita_mano,
                'compensazione_latenza': compensazione
            }
            
            if triggered:
                suono = self.mappa_suono('mano', True, intensity)
                if suono:
                    risultati['suoni'].append(suono)
        
        # Processa trigger microfono
        if amplitude_microfono is not None:
            triggered, intensity = self.trigger_microfono(amplitude_microfono)
            picco = self.calcola_picco([amplitude_microfono])
            
            risultati['triggers']['microfono'] = {
                'triggered': triggered,
                'intensity': intensity,
                'amplitude': amplitude_microfono,
                'picco': picco
            }
            
            if triggered:
                suono = self.mappa_suono('microfono', True, intensity)
                if suono:
                    risultati['suoni'].append(suono)
        
        return risultati
    
    def get_statistics(self) -> Dict:
        """Restituisce statistiche del sistema"""
        return {
            'latenza_totale': self.calcola_latenza_totale(),
            'soglie': self.thresholds.copy(),
            'volume_range': self.volume_range.copy(),
            'buffer_sizes': {
                'acceleration': len(self.acceleration_buffer),
                'velocity': len(self.velocity_buffer),
                'audio': len(self.audio_buffer)
            }
        }

