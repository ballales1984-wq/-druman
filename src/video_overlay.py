"""
Visualizzazione video live con overlay dei pad
Mostra il video della webcam con rettangoli verdi per i pad attivi
"""
import pygame
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from src.config import DRUM_ZONES, COLORS, WINDOW_WIDTH, WINDOW_HEIGHT

class VideoOverlay:
    """Classe per visualizzare video live con overlay dei pad"""
    
    def __init__(self, screen: pygame.Surface, camera_width: int = 640, camera_height: int = 480):
        """
        Inizializza la visualizzazione video
        
        Args:
            screen: Superficie Pygame dove disegnare
            camera_width: Larghezza video camera
            camera_height: Altezza video camera
        """
        self.screen = screen
        self.camera_width = camera_width
        self.camera_height = camera_height
        
        # Calcola scaling per adattare video alla finestra
        self.scale_x = WINDOW_WIDTH / camera_width
        self.scale_y = WINDOW_HEIGHT / camera_height
        self.scale = min(self.scale_x, self.scale_y)
        
        # Dimensioni video scalato
        self.video_width = int(camera_width * self.scale)
        self.video_height = int(camera_height * self.scale)
        
        # Offset per centrare
        self.offset_x = (WINDOW_WIDTH - self.video_width) // 2
        self.offset_y = (WINDOW_HEIGHT - self.video_height) // 2
        
        # Stato pad attivi
        self.active_pads = {}  # {drum_name: (active, intensity)}
        
        # Font per etichette
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
    
    def update_frame(self, frame: np.ndarray):
        """
        Aggiorna il frame video
        
        Args:
            frame: Frame OpenCV (BGR)
        """
        # Converti BGR a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Ruota e specchia (opzionale)
        frame_rgb = cv2.flip(frame_rgb, 1)  # Specchia orizzontalmente
        
        # Converti a Pygame surface
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        
        # Scala il frame
        frame_scaled = pygame.transform.scale(frame_surface, (self.video_width, self.video_height))
        
        # Disegna frame
        self.screen.blit(frame_scaled, (self.offset_x, self.offset_y))
    
    def set_active_pad(self, drum_name: str, active: bool, intensity: float = 1.0):
        """
        Imposta stato di un pad
        
        Args:
            drum_name: Nome del componente (kick, snare, etc.)
            active: Se il pad è attivo
            intensity: Intensità (0-1)
        """
        self.active_pads[drum_name] = (active, intensity)
    
    def draw_pad_overlay(self, drum_name: str, position: Tuple[int, int], size: Tuple[int, int]):
        """
        Disegna overlay di un pad sul video
        
        Args:
            drum_name: Nome del componente
            position: Posizione (x, y) in pixel video
            size: Dimensione (width, height) in pixel video
        """
        # Scala posizione e dimensione
        x = int(position[0] * self.scale) + self.offset_x
        y = int(position[1] * self.scale) + self.offset_y
        w = int(size[0] * self.scale)
        h = int(size[1] * self.scale)
        
        # Ottieni stato pad
        active, intensity = self.active_pads.get(drum_name, (False, 0.0))
        
        # Colore in base allo stato
        if active:
            # Verde brillante quando attivo
            color = (0, 255, 0)  # Verde
            alpha = int(150 + 105 * intensity)  # Trasparenza basata su intensità
        else:
            # Grigio quando inattivo
            color = (100, 100, 100)
            alpha = 80
        
        # Crea superficie semi-trasparente
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*color, alpha), (0, 0, w, h), 3)
        
        # Riempimento semi-trasparente
        if active:
            fill_overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(fill_overlay, (*color, alpha // 3), (0, 0, w, h))
            self.screen.blit(fill_overlay, (x, y))
        
        # Bordo
        self.screen.blit(overlay, (x, y))
        
        # Etichetta
        label = self.font.render(drum_name.upper(), True, (255, 255, 255))
        label_bg = pygame.Surface((label.get_width() + 4, label.get_height() + 4), pygame.SRCALPHA)
        label_bg.fill((0, 0, 0, 180))
        self.screen.blit(label_bg, (x + 2, y + 2))
        self.screen.blit(label, (x + 4, y + 4))
        
        # Intensità (se attivo)
        if active:
            intensity_text = self.font_small.render(f"{int(intensity * 100)}%", True, (255, 255, 0))
            self.screen.blit(intensity_text, (x + w - 40, y + h - 20))
    
    def draw_all_pads(self, keypoints: Optional[Dict] = None, pad_positions: Optional[Dict] = None):
        """
        Disegna tutti i pad basandosi sulle zone configurate
        I pad sono disposti in colonna verticale al centro
        
        Args:
            keypoints: Keypoints MediaPipe (opzionale, per posizionamento dinamico)
        """
        # Usa posizioni dinamiche se disponibili, altrimenti usa config
        zones_to_use = pad_positions if pad_positions else DRUM_ZONES
        
        for drum_name, zone_config in zones_to_use.items():
            center = zone_config['center']
            radius = zone_config['radius']
            
            # Converti coordinate normalizzate (0-1) a pixel video
            x = int(center[0] * self.camera_width)
            y = int(center[1] * self.camera_height)
            
            # Dimensioni pad basate sul tipo
            if drum_name == 'snare':
                # Snare a DESTRA (INVERTITO) - pad circolare/quadrato
                pad_size = int(self.camera_width * 0.15)
                if 'x_range' in zone_config and 'y_range' in zone_config:
                    x_min, x_max = zone_config['x_range']
                    y_min, y_max = zone_config['y_range']
                    x = int(((x_min + x_max) / 2) * self.camera_width)
                    y = int(((y_min + y_max) / 2) * self.camera_height)
                self.draw_pad_overlay(drum_name, (x - pad_size // 2, y - pad_size // 2), (pad_size, pad_size))
            
            elif drum_name == 'hihat':
                # Hi-Hat a SINISTRA (INVERTITO) - pad circolare/quadrato
                pad_size = int(self.camera_width * 0.15)
                if 'x_range' in zone_config and 'y_range' in zone_config:
                    x_min, x_max = zone_config['x_range']
                    y_min, y_max = zone_config['y_range']
                    x = int(((x_min + x_max) / 2) * self.camera_width)
                    y = int(((y_min + y_max) / 2) * self.camera_height)
                self.draw_pad_overlay(drum_name, (x - pad_size // 2, y - pad_size // 2), (pad_size, pad_size))
            
            elif drum_name == 'kick':
                # Kick in BASSO CENTRO - pad rettangolare orizzontale
                pad_width = int(self.camera_width * 0.25)
                pad_height = int(self.camera_height * 0.15)
                if 'x_range' in zone_config and 'y_range' in zone_config:
                    x_min, x_max = zone_config['x_range']
                    y_min, y_max = zone_config['y_range']
                    x = int(((x_min + x_max) / 2) * self.camera_width)
                    y = int(((y_min + y_max) / 2) * self.camera_height)
                self.draw_pad_overlay(drum_name, (x - pad_width // 2, y - pad_height // 2), (pad_width, pad_height))
            
            else:
                # Fallback per altri pad
                pad_size = int(self.camera_width * 0.12)
                self.draw_pad_overlay(drum_name, (x - pad_size // 2, y - pad_size // 2), (pad_size, pad_size))
    
    def draw_info(self, fps: float, active_count: int):
        """
        Disegna informazioni overlay
        
        Args:
            fps: FPS corrente
            active_count: Numero di pad attivi
        """
        # FPS
        fps_text = self.font_small.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
        fps_bg = pygame.Surface((fps_text.get_width() + 4, fps_text.get_height() + 4), pygame.SRCALPHA)
        fps_bg.fill((0, 0, 0, 180))
        self.screen.blit(fps_bg, (10, 10))
        self.screen.blit(fps_text, (12, 12))
        
        # Pad attivi
        active_text = self.font_small.render(f"Pad Attivi: {active_count}", True, (0, 255, 0))
        active_bg = pygame.Surface((active_text.get_width() + 4, active_text.get_height() + 4), pygame.SRCALPHA)
        active_bg.fill((0, 0, 0, 180))
        self.screen.blit(active_bg, (10, 35))
        self.screen.blit(active_text, (12, 37))
    
    def clear(self):
        """Pulisce lo schermo"""
        self.screen.fill(COLORS['background'])

