"""
Sistema di calibrazione interattiva per posizionare e ridimensionare i pad
Permette all'utente di decidere dove mettere i pad e la loro dimensione
"""
import pygame
import numpy as np
from typing import Dict, Optional, Tuple
from src.config import DRUM_ZONES

class PadCalibrator:
    """Calibratore interattivo per posizionare e ridimensionare i pad"""
    
    def __init__(self, screen, camera_width: int, camera_height: int):
        """
        Inizializza il calibratore
        
        Args:
            screen: Superficie pygame per disegnare
            camera_width: Larghezza video
            camera_height: Altezza video
        """
        self.screen = screen
        self.camera_width = camera_width
        self.camera_height = camera_height
        
        # Stato calibrazione
        self.calibrating = False
        self.current_pad = None
        self.pad_index = 0
        self.pad_names = ['snare', 'hihat', 'kick']
        
        # Posizioni e dimensioni pad (inizializza da config)
        self.pad_configs = {}
        for pad_name in self.pad_names:
            if pad_name in DRUM_ZONES:
                config = DRUM_ZONES[pad_name].copy()
                # Converti center in pixel
                center = config['center']
                self.pad_configs[pad_name] = {
                    'center_px': (int(center[0] * camera_width), int(center[1] * camera_height)),
                    'size': 100,  # Dimensione iniziale in pixel
                    'x_range': config.get('x_range', (0.0, 1.0)),
                    'y_range': config.get('y_range', (0.0, 1.0))
                }
        
        # Font per testo
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Stato drag
        self.dragging = False
        self.drag_offset = (0, 0)
        self.resizing = False
        self.resize_start_size = 0
    
    def start_calibration(self):
        """Inizia la calibrazione"""
        self.calibrating = True
        self.pad_index = 0
        self.current_pad = self.pad_names[0]
        print(f"[CALIBRAZIONE] Iniziata - Pad: {self.current_pad}")
        print("  Usa MOUSE per spostare e ridimensionare")
        print("  CLICK SINISTRO: Sposta pad")
        print("  CLICK DESTRO: Ridimensiona pad")
        print("  SPACE: Prossimo pad")
        print("  ENTER: Salva e termina")
        print("  ESC: Annulla")
    
    def stop_calibration(self):
        """Termina la calibrazione"""
        self.calibrating = False
        self.current_pad = None
    
    def is_calibrating(self) -> bool:
        """Verifica se sta calibrando"""
        return self.calibrating
    
    def handle_mouse_down(self, pos: Tuple[int, int], button: int):
        """
        Gestisce click mouse
        
        Args:
            pos: Posizione mouse (x, y)
            button: Bottone mouse (1=sinistro, 3=destro)
        """
        if not self.calibrating or not self.current_pad:
            return
        
        pad_config = self.pad_configs[self.current_pad]
        center = pad_config['center_px']
        size = pad_config['size']
        
        # Calcola distanza dal centro
        dx = pos[0] - center[0]
        dy = pos[1] - center[1]
        distance = np.sqrt(dx*dx + dy*dy)
        
        if button == 1:  # Click sinistro - sposta
            if distance < size / 2:
                self.dragging = True
                self.drag_offset = (dx, dy)
        elif button == 3:  # Click destro - ridimensiona
            if distance < size / 2:
                self.resizing = True
                self.resize_start_size = size
    
    def handle_mouse_up(self):
        """Gestisce rilascio mouse"""
        self.dragging = False
        self.resizing = False
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """
        Gestisce movimento mouse
        
        Args:
            pos: Posizione mouse (x, y)
        """
        if not self.calibrating or not self.current_pad:
            return
        
        pad_config = self.pad_configs[self.current_pad]
        
        if self.dragging:
            # Sposta il pad
            pad_config['center_px'] = (
                pos[0] - self.drag_offset[0],
                pos[1] - self.drag_offset[1]
            )
            # Limita ai bordi dello schermo
            pad_config['center_px'] = (
                max(50, min(self.camera_width - 50, pad_config['center_px'][0])),
                max(50, min(self.camera_height - 50, pad_config['center_px'][1]))
            )
        elif self.resizing:
            # Ridimensiona il pad
            center = pad_config['center_px']
            dx = pos[0] - center[0]
            dy = pos[1] - center[1]
            distance = np.sqrt(dx*dx + dy*dy)
            new_size = int(distance * 2)
            pad_config['size'] = max(30, min(300, new_size))
    
    def handle_key(self, key) -> bool:
        """
        Gestisce input tastiera
        
        Args:
            key: Codice tasto premuto
        
        Returns:
            True se ha gestito il tasto
        """
        if not self.calibrating:
            return False
        
        if key == pygame.K_SPACE:
            # Prossimo pad
            self.pad_index = (self.pad_index + 1) % len(self.pad_names)
            self.current_pad = self.pad_names[self.pad_index]
            print(f"[CALIBRAZIONE] Pad: {self.current_pad}")
            return True
        elif key == pygame.K_RETURN:
            # Salva e termina
            self._save_configuration()
            self.stop_calibration()
            print("[CALIBRAZIONE] Configurazione salvata!")
            return True
        elif key == pygame.K_ESCAPE:
            # Annulla
            self.stop_calibration()
            print("[CALIBRAZIONE] Annullata")
            return True
        
        return False
    
    def _save_configuration(self):
        """Salva la configurazione dei pad"""
        # Aggiorna DRUM_ZONES con le nuove posizioni
        for pad_name, pad_config in self.pad_configs.items():
            if pad_name in DRUM_ZONES:
                # Converti pixel in coordinate normalizzate (0-1)
                center_px = pad_config['center_px']
                center_norm = np.array([
                    center_px[0] / self.camera_width,
                    center_px[1] / self.camera_height,
                    0.0
                ])
                
                # Calcola range basato su dimensione
                size_norm = pad_config['size'] / min(self.camera_width, self.camera_height)
                half_size = size_norm / 2
                
                x_range = (
                    max(0.0, center_norm[0] - half_size),
                    min(1.0, center_norm[0] + half_size)
                )
                y_range = (
                    max(0.0, center_norm[1] - half_size),
                    min(1.0, center_norm[1] + half_size)
                )
                
                # Aggiorna configurazione
                DRUM_ZONES[pad_name]['center'] = center_norm
                DRUM_ZONES[pad_name]['x_range'] = x_range
                DRUM_ZONES[pad_name]['y_range'] = y_range
                
                print(f"  {pad_name}: center=({center_norm[0]:.2f}, {center_norm[1]:.2f}), "
                      f"size={pad_config['size']}px, "
                      f"x_range=({x_range[0]:.2f}, {x_range[1]:.2f}), "
                      f"y_range=({y_range[0]:.2f}, {y_range[1]:.2f})")
    
    def draw_calibration(self):
        """Disegna l'interfaccia di calibrazione"""
        if not self.calibrating or not self.current_pad:
            return
        
        # Disegna tutti i pad
        for pad_name, pad_config in self.pad_configs.items():
            center = pad_config['center_px']
            size = pad_config['size']
            
            # Colore: verde per pad corrente, grigio per altri
            if pad_name == self.current_pad:
                color = (0, 255, 0)  # Verde
                border_color = (255, 255, 0)  # Giallo per bordo
                border_width = 3
            else:
                color = (100, 100, 100)  # Grigio
                border_color = (50, 50, 50)
                border_width = 1
            
            # Disegna cerchio/rettangolo
            if pad_name == 'kick':
                # Kick: rettangolo
                rect = pygame.Rect(
                    center[0] - size // 2,
                    center[1] - size // 3,
                    size,
                    size * 2 // 3
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, border_color, rect, border_width)
            else:
                # Snare e Hi-Hat: cerchio
                pygame.draw.circle(self.screen, color, center, size // 2)
                pygame.draw.circle(self.screen, border_color, center, size // 2, border_width)
            
            # Etichetta
            label = self.font_small.render(pad_name.upper(), True, (255, 255, 255))
            label_rect = label.get_rect(center=(center[0], center[1] - size // 2 - 20))
            self.screen.blit(label, label_rect)
        
        # Istruzioni
        instructions = [
            f"Calibrazione: {self.current_pad.upper()}",
            "CLICK SINISTRO: Sposta pad",
            "CLICK DESTRO: Ridimensiona",
            "SPACE: Prossimo pad",
            "ENTER: Salva",
            "ESC: Annulla"
        ]
        
        y_offset = 10
        for i, text in enumerate(instructions):
            if i == 0:
                text_surface = self.font.render(text, True, (255, 255, 0))
            else:
                text_surface = self.font_small.render(text, True, (255, 255, 255))
            
            bg = pygame.Surface((text_surface.get_width() + 8, text_surface.get_height() + 4), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 200))
            self.screen.blit(bg, (10, y_offset))
            self.screen.blit(text_surface, (12, y_offset + 2))
            y_offset += text_surface.get_height() + 6
    
    def get_pad_configs(self) -> Dict:
        """Restituisce le configurazioni dei pad"""
        return self.pad_configs.copy()

