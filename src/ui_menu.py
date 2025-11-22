"""
Modulo per il menu di configurazione e controlli
"""
import pygame
import numpy as np
from typing import Dict, Optional, Callable
from src.config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT

class UIMenu:
    """Menu di interfaccia utente per configurazioni"""
    
    def __init__(self, screen):
        """
        Inizializza il menu UI
        
        Args:
            screen: Superficie Pygame dove disegnare
        """
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.menu_active = False
        self.current_page = 'main'
        
        # Configurazioni modificabili
        self.settings = {
            'metronome_enabled': False,
            'metronome_bpm': 120,
            'master_volume': 0.7,
            'velocity_threshold': 0.3,
            'show_camera': False,
            'calibration_mode': False
        }
        
        # Callback per le azioni
        self.callbacks = {}
    
    def register_callback(self, action: str, callback: Callable):
        """Registra un callback per un'azione"""
        self.callbacks[action] = callback
    
    def toggle_menu(self):
        """Attiva/disattiva il menu"""
        self.menu_active = not self.menu_active
        if self.menu_active:
            self.current_page = 'main'
    
    def is_active(self) -> bool:
        """Verifica se il menu è attivo"""
        return self.menu_active
    
    def handle_key(self, key: int) -> bool:
        """
        Gestisce l'input da tastiera
        
        Returns:
            True se l'input è stato gestito
        """
        if not self.menu_active:
            return False
        
        if key == pygame.K_ESCAPE:
            self.menu_active = False
            return True
        elif key == pygame.K_m:
            if self.current_page == 'main':
                self.current_page = 'metronome'
            elif self.current_page == 'metronome':
                self.current_page = 'main'
            return True
        elif key == pygame.K_v:
            if self.current_page == 'main':
                self.current_page = 'volume'
            elif self.current_page == 'volume':
                self.current_page = 'main'
            return True
        elif key == pygame.K_c:
            if self.current_page == 'main':
                self.current_page = 'calibration'
            elif self.current_page == 'calibration':
                self.current_page = 'main'
            return True
        
        # Controlli per metronomo
        if self.current_page == 'metronome':
            if key == pygame.K_SPACE:
                self.settings['metronome_enabled'] = not self.settings['metronome_enabled']
                if 'toggle_metronome' in self.callbacks:
                    self.callbacks['toggle_metronome'](self.settings['metronome_enabled'])
                return True
            elif key == pygame.K_UP:
                self.settings['metronome_bpm'] = min(200, self.settings['metronome_bpm'] + 5)
                if 'set_metronome_bpm' in self.callbacks:
                    self.callbacks['set_metronome_bpm'](self.settings['metronome_bpm'])
                return True
            elif key == pygame.K_DOWN:
                self.settings['metronome_bpm'] = max(60, self.settings['metronome_bpm'] - 5)
                if 'set_metronome_bpm' in self.callbacks:
                    self.callbacks['set_metronome_bpm'](self.settings['metronome_bpm'])
                return True
        
        # Controlli per volume
        if self.current_page == 'volume':
            if key == pygame.K_UP:
                self.settings['master_volume'] = min(1.0, self.settings['master_volume'] + 0.1)
                if 'set_master_volume' in self.callbacks:
                    self.callbacks['set_master_volume'](self.settings['master_volume'])
                return True
            elif key == pygame.K_DOWN:
                self.settings['master_volume'] = max(0.0, self.settings['master_volume'] - 0.1)
                if 'set_master_volume' in self.callbacks:
                    self.callbacks['set_master_volume'](self.settings['master_volume'])
                return True
        
        # Controlli per calibrazione
        if self.current_page == 'calibration':
            if key == pygame.K_SPACE:
                if 'start_calibration' in self.callbacks:
                    self.callbacks['start_calibration']()
                return True
        
        return False
    
    def draw(self):
        """Disegna il menu"""
        if not self.menu_active:
            return
        
        # Sfondo semi-trasparente
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Disegna il menu in base alla pagina corrente
        if self.current_page == 'main':
            self._draw_main_menu()
        elif self.current_page == 'metronome':
            self._draw_metronome_menu()
        elif self.current_page == 'volume':
            self._draw_volume_menu()
        elif self.current_page == 'calibration':
            self._draw_calibration_menu()
    
    def _draw_main_menu(self):
        """Disegna il menu principale"""
        y = 200
        spacing = 60
        
        title = self.font_large.render("MENU", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        options = [
            ("M - Metronomo", self.settings['metronome_enabled']),
            ("V - Volume", None),
            ("C - Calibrazione", None),
            ("ESC - Chiudi Menu", None)
        ]
        
        for text, status in options:
            color = (200, 200, 200) if status is None else ((100, 255, 100) if status else (255, 100, 100))
            surface = self.font_medium.render(text, True, color)
            rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(surface, rect)
            y += spacing
    
    def _draw_metronome_menu(self):
        """Disegna il menu del metronomo"""
        y = 150
        
        title = self.font_large.render("METRONOMO", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(title, title_rect)
        y += 80
        
        # Stato
        status_text = "ATTIVO" if self.settings['metronome_enabled'] else "DISATTIVO"
        status_color = (100, 255, 100) if self.settings['metronome_enabled'] else (255, 100, 100)
        status_surface = self.font_medium.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(status_surface, status_rect)
        y += 60
        
        # BPM
        bpm_text = f"BPM: {self.settings['metronome_bpm']}"
        bpm_surface = self.font_large.render(bpm_text, True, (255, 255, 255))
        bpm_rect = bpm_surface.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(bpm_surface, bpm_rect)
        y += 100
        
        # Controlli
        controls = [
            "SPACE - Attiva/Disattiva",
            "↑ - Aumenta BPM",
            "↓ - Diminuisci BPM",
            "M - Torna al menu"
        ]
        
        for control in controls:
            surface = self.font_small.render(control, True, (200, 200, 200))
            rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(surface, rect)
            y += 40
    
    def _draw_volume_menu(self):
        """Disegna il menu del volume"""
        y = 150
        
        title = self.font_large.render("VOLUME", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(title, title_rect)
        y += 80
        
        # Volume attuale
        volume_percent = int(self.settings['master_volume'] * 100)
        volume_text = f"{volume_percent}%"
        volume_surface = self.font_large.render(volume_text, True, (255, 255, 255))
        volume_rect = volume_surface.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(volume_surface, volume_rect)
        y += 60
        
        # Barra del volume
        bar_width = 400
        bar_height = 30
        bar_x = (WINDOW_WIDTH - bar_width) // 2
        bar_y = y
        
        # Sfondo barra
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Volume attuale
        fill_width = int(bar_width * self.settings['master_volume'])
        pygame.draw.rect(self.screen, (100, 200, 100), (bar_x, bar_y, fill_width, bar_height))
        
        # Bordo
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        y += 80
        
        # Controlli
        controls = [
            "↑ - Aumenta Volume",
            "↓ - Diminuisci Volume",
            "V - Torna al menu"
        ]
        
        for control in controls:
            surface = self.font_small.render(control, True, (200, 200, 200))
            rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(surface, rect)
            y += 40
    
    def _draw_calibration_menu(self):
        """Disegna il menu di calibrazione"""
        y = 150
        
        title = self.font_large.render("CALIBRAZIONE", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, y))
        self.screen.blit(title, title_rect)
        y += 80
        
        info_text = [
            "La calibrazione aiuta il sistema",
            "a riconoscere meglio i tuoi movimenti.",
            "",
            "Muoviti naturalmente durante",
            "la calibrazione."
        ]
        
        for text in info_text:
            if text:
                surface = self.font_small.render(text, True, (200, 200, 200))
                rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
                self.screen.blit(surface, rect)
            y += 30
        
        y += 20
        
        # Controlli
        controls = [
            "SPACE - Avvia Calibrazione",
            "C - Torna al menu"
        ]
        
        for control in controls:
            surface = self.font_medium.render(control, True, (100, 200, 255))
            rect = surface.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(surface, rect)
            y += 50

