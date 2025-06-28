import pygame
from core.Settings import *

class DeleteWindow:
    def __init__(self, deck_name):
        self.deck_name = deck_name
        self.width = 400
        self.height = 180
        self.font = pygame.font.Font(font_path, 32)
        self.button_font = pygame.font.Font(font_path, 28)

        # Wyśrodkuj okno
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        self.rect = pygame.Rect(
            (screen_rect.width - self.width) // 2,
            (screen_rect.height - self.height) // 2,
            self.width,
            self.height
        )

        # Przyciski
        self.yes_rect = pygame.Rect(self.rect.centerx - 120, self.rect.bottom - 60, 90, 40)
        self.no_rect = pygame.Rect(self.rect.centerx + 30, self.rect.bottom - 60, 90, 40)

    def draw(self, screen):
        # Tło okna
        pygame.draw.rect(screen, (255, 240, 240), self.rect, border_radius=12)
        pygame.draw.rect(screen, (150, 100, 100), self.rect, 2, border_radius=12)

        # Tekst pytania
        question = f"Do you want to delete deck \"{self.deck_name}\"?"
        text_surf = self.font.render(question, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.top + 50))
        screen.blit(text_surf, text_rect)

        # Przycisk YES
        pygame.draw.rect(screen, (220, 250, 220), self.yes_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 160, 100), self.yes_rect, 2, border_radius=8)
        yes_text = self.button_font.render("Yes", True, (0, 0, 0))
        screen.blit(yes_text, yes_text.get_rect(center=self.yes_rect.center))

        # Przycisk NO
        pygame.draw.rect(screen, (250, 220, 220), self.no_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 100, 100), self.no_rect, 2, border_radius=8)
        no_text = self.button_font.render("No", True, (0, 0, 0))
        screen.blit(no_text, no_text.get_rect(center=self.no_rect.center))

