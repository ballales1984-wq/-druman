"""
Modulo per la visualizzazione 3D dell'ambiente virtuale
"""
import pygame
import numpy as np
from typing import Dict, Optional, Tuple
import sys
import os

# Aggiungi il percorso del progetto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import DRUM_ZONES, COLORS, WINDOW_WIDTH, WINDOW_HEIGHT

class VirtualEnvironment:
    """Classe per visualizzare l'ambiente virtuale 3D"""
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        """
        Inizializza l'ambiente virtuale
        
        Args:
            width: Larghezza della finestra
            height: Altezza della finestra
        """
        self.width = width
        self.height = height
        
        # Inizializza Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("DrumMan - Virtual Drum Machine")
        self.clock = pygame.time.Clock()
        
        # Font per il testo
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Stato delle zone attive
        self.active_zones = set()
        self.zone_activation_times = {}  # Per animazioni
        
        # Posizioni dell'utente (coordinate normalizzate)
        self.user_positions = {}
        
        # Animazioni
        self.hit_effects = []  # Lista di effetti visivi per i colpi
        self.frame_count = 0
    
    def project_3d_to_2d(self, point_3d: np.ndarray, camera_pos: np.ndarray = np.array([0, 0, 2])) -> Tuple[int, int]:
        """
        Proietta un punto 3D nello schermo 2D (proiezione ortografica semplificata)
        
        Args:
            point_3d: Punto 3D in coordinate normalizzate (0-1)
            camera_pos: Posizione della camera
        
        Returns:
            Coordinate (x, y) nello schermo
        """
        # Converti coordinate normalizzate in coordinate 3D
        x = (point_3d[0] - 0.5) * 4  # Scala da 0-1 a -2 a 2
        y = (0.5 - point_3d[1]) * 4  # Inverti Y
        z = point_3d[2] * 2
        
        # Proiezione ortografica semplificata
        scale = 200  # Fattore di scala
        screen_x = int(self.width / 2 + x * scale)
        screen_y = int(self.height / 2 + y * scale - z * scale)
        
        return screen_x, screen_y
    
    def draw_drum_zone(self, zone_name: str, zone_config: Dict, is_active: bool = False):
        """
        Disegna una zona della batteria con animazioni
        
        Args:
            zone_name: Nome della zona
            zone_config: Configurazione della zona
            is_active: Se la zona è attualmente attiva
        """
        center_2d = self.project_3d_to_2d(zone_config['center'])
        base_radius = int(zone_config['radius'] * 400)  # Scala il raggio
        
        # Animazione quando attiva
        if is_active:
            if zone_name not in self.zone_activation_times:
                self.zone_activation_times[zone_name] = self.frame_count
            
            time_since_activation = self.frame_count - self.zone_activation_times[zone_name]
            pulse = 1.0 + 0.3 * np.sin(time_since_activation * 0.3)  # Pulsazione
            radius = int(base_radius * pulse)
            color = COLORS['drum_zone_active']
            
            # Effetto esplosione quando appena colpita
            if time_since_activation < 5:
                explosion_radius = int(base_radius * (1 + time_since_activation * 0.2))
                alpha = max(0, 255 - time_since_activation * 50)
                explosion_color = (*color[:3], alpha) if len(color) == 4 else color
                pygame.draw.circle(self.screen, color, center_2d, explosion_radius, 2)
        else:
            radius = base_radius
            color = COLORS['drum_zone']
            if zone_name in self.zone_activation_times:
                del self.zone_activation_times[zone_name]
        
        # Disegna il cerchio principale con gradiente
        pygame.draw.circle(self.screen, color, center_2d, radius, 3)
        
        # Disegna cerchi concentrici per effetto 3D
        for i in range(2, 0, -1):
            inner_radius = int(radius * (i * 0.3))
            inner_color = tuple(c // (4 - i) for c in color[:3])
            pygame.draw.circle(self.screen, inner_color, center_2d, inner_radius, 1)
        
        # Disegna il cerchio interno (zona di trigger)
        trigger_radius = int(zone_config['trigger_distance'] * 400)
        pygame.draw.circle(self.screen, color, center_2d, trigger_radius, 1)
        
        # Etichetta con sfondo
        text = self.small_font.render(zone_name.upper(), True, color)
        text_rect = text.get_rect(center=(center_2d[0], center_2d[1] - radius - 20))
        
        # Sfondo semi-trasparente per leggibilità
        bg_rect = text_rect.inflate(10, 5)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        self.screen.blit(bg_surface, bg_rect)
        self.screen.blit(text, text_rect)
    
    def draw_user(self, key_points: Dict):
        """
        Disegna la rappresentazione dell'utente con miglioramenti visivi
        
        Args:
            key_points: Dizionario con le posizioni delle articolazioni
        """
        # Disegna le connessioni prima (sotto i punti)
        connections = [
            (('left_wrist', 'right_wrist'), 2),
            (('left_wrist', 'nose'), 1),
            (('right_wrist', 'nose'), 1),
            (('left_ankle', 'right_ankle'), 2),
        ]
        
        for (point1_name, point2_name), width in connections:
            if point1_name in key_points and point2_name in key_points:
                pos1 = self.project_3d_to_2d(key_points[point1_name])
                pos2 = self.project_3d_to_2d(key_points[point2_name])
                color = tuple(c // 2 for c in COLORS['user'])  # Più scuro per le linee
                pygame.draw.line(self.screen, color, pos1, pos2, width)
        
        # Disegna i punti chiave con dimensioni diverse
        point_sizes = {
            'wrist': 10,
            'ankle': 8,
            'nose': 6
        }
        
        for point_name, point_3d in key_points.items():
            screen_pos = self.project_3d_to_2d(point_3d)
            
            # Determina la dimensione
            size = 8
            for key, value in point_sizes.items():
                if key in point_name:
                    size = value
                    break
            
            # Disegna cerchio con bordo
            pygame.draw.circle(self.screen, COLORS['user'], screen_pos, size)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, size, 2)
            
            # Etichetta per i polsi (più importanti per la batteria)
            if 'wrist' in point_name:
                label = 'L' if 'left' in point_name else 'R'
                text = self.small_font.render(label, True, (255, 255, 255))
                text_bg = pygame.Surface((text.get_width() + 4, text.get_height() + 4))
                text_bg.set_alpha(200)
                text_bg.fill((0, 0, 0))
                self.screen.blit(text_bg, (screen_pos[0] + 12, screen_pos[1] - 12))
                self.screen.blit(text, (screen_pos[0] + 14, screen_pos[1] - 10))
    
    def draw_grid(self):
        """Disegna una griglia di riferimento"""
        grid_spacing = 50
        grid_color = COLORS['grid']
        
        # Linee verticali
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height), 1)
        
        # Linee orizzontali
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y), 1)
    
    def update(self, key_points: Optional[Dict] = None, active_zones: Optional[set] = None, 
               fps: Optional[float] = None, show_info: bool = True):
        """
        Aggiorna e disegna l'ambiente virtuale
        
        Args:
            key_points: Punti chiave dell'utente
            active_zones: Set di zone attualmente attive
            fps: FPS corrente (opzionale)
            show_info: Mostra informazioni di debug
        """
        self.frame_count += 1
        
        # Sfondo
        self.screen.fill(COLORS['background'])
        
        # Griglia
        self.draw_grid()
        
        # Aggiorna zone attive
        if active_zones is not None:
            self.active_zones = active_zones
        
        # Disegna tutte le zone della batteria
        for zone_name, zone_config in DRUM_ZONES.items():
            is_active = zone_name in self.active_zones
            self.draw_drum_zone(zone_name, zone_config, is_active)
        
        # Disegna l'utente
        if key_points is not None:
            self.draw_user(key_points)
        
        # Informazioni di debug
        if show_info:
            info_text = [
                f"Zone attive: {len(self.active_zones)}",
                "TAB - Menu | ESC - Esci"
            ]
            
            if fps is not None:
                info_text.insert(1, f"FPS: {fps:.1f}")
            
            y_offset = 10
            for text in info_text:
                # Sfondo semi-trasparente per leggibilità
                surface = self.small_font.render(text, True, (255, 255, 255))
                bg = pygame.Surface((surface.get_width() + 8, surface.get_height() + 4))
                bg.set_alpha(180)
                bg.fill((0, 0, 0))
                self.screen.blit(bg, (6, y_offset - 2))
                self.screen.blit(surface, (10, y_offset))
                y_offset += 25
        
        # Aggiorna lo schermo
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS
    
    def check_events(self) -> Tuple[bool, Optional[int]]:
        """
        Controlla gli eventi (tastiera, mouse, etc.)
        
        Returns:
            Tuple (continua, key_pressed): 
            - continua: True se l'applicazione deve continuare
            - key_pressed: Codice del tasto premuto o None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, None
                else:
                    return True, event.key
        return True, None
    
    def close(self):
        """Chiude l'ambiente virtuale"""
        pygame.quit()

