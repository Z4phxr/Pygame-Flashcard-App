import pygame
from typing import Optional
from core.Settings import *
from ui.Deck_container import DeckContainer


class AddDeckWindow:
    """
    Represents a modal window for creating a new deck.
    Handles input text, cursor blinking, rendering, and basic button interaction.
    """

    def __init__(self):
        self.width = 420
        self.height = 200

        # Fonts
        self.font = pygame.font.Font(font_path, 32)
        self.button_font = pygame.font.Font(font_path, 28)
        self.input_font = pygame.font.Font(font_path, 40)
        self.small_font = pygame.font.Font(font_path, 18)

        # Input state
        self.text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.name_accepted = True

        # Main window position
        screen = pygame.display.get_surface()
        screen_rect = screen.get_rect()
        self.rect = pygame.Rect(
            (screen_rect.width - self.width) // 2,
            (screen_rect.height - self.height) // 2,
            self.width,
            self.height
        )

        # Input field rectangle
        self.input_rect = pygame.Rect(self.rect.x + 30, self.rect.y + 70, self.width - 60, 50)

        # Buttons
        self.create_rect = pygame.Rect(self.rect.centerx - 120, self.rect.bottom - 60, 90, 40)
        self.cancel_rect = pygame.Rect(self.rect.centerx + 30, self.rect.bottom - 60, 90, 40)

    def update_cursor(self, dt: int) -> None:
        """
        Update the blinking cursor timer.

        Args:
            dt (int): Milliseconds since last update.
        """
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the add deck window and all UI elements.

        Args:
            screen (pygame.Surface): The surface to draw onto.
        """
        # Background
        pygame.draw.rect(screen, (255, 240, 240), self.rect, border_radius=12)
        pygame.draw.rect(screen, (150, 100, 100), self.rect, 2, border_radius=12)

        # Prompt text
        prompt = self.font.render("Enter name for new deck:", True, (0, 0, 0))
        screen.blit(prompt, (self.rect.x + 30, self.rect.y + 25))

        # Input field
        pygame.draw.rect(screen, (255, 255, 255), self.input_rect, border_radius=8)
        pygame.draw.rect(screen, (150, 100, 100), self.input_rect, 2, border_radius=8)

        # Blinking cursor
        display_text = self.text + ("|" if self.cursor_visible else "")
        text_surface = self.input_font.render(display_text, True, (0, 0, 0))
        screen.blit(text_surface, (self.input_rect.x + 10, self.input_rect.y + 1))

        # Error message if name not accepted
        if not self.name_accepted:
            error_text = self.small_font.render("Deck with this name already exists", True, (200, 30, 30))
            error_rect = error_text.get_rect(center=(self.input_rect.centerx, self.input_rect.bottom + 20))
            screen.blit(error_text, error_rect)

        # Create button
        pygame.draw.rect(screen, (220, 250, 220), self.create_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 160, 100), self.create_rect, 2, border_radius=8)
        create_text = self.button_font.render("Create", True, (0, 0, 0))
        screen.blit(create_text, create_text.get_rect(center=self.create_rect.center))

        # Cancel button
        pygame.draw.rect(screen, (250, 220, 220), self.cancel_rect, border_radius=8)
        pygame.draw.rect(screen, (180, 100, 100), self.cancel_rect, 2, border_radius=8)
        cancel_text = self.button_font.render("Cancel", True, (0, 0, 0))
        screen.blit(cancel_text, cancel_text.get_rect(center=self.cancel_rect.center))

    def handle_click(self, pos: tuple[int, int]) -> Optional[str]:
        """
        Check if the user clicked a button and return the corresponding action.

        Args:
            pos (tuple): Mouse position.

        Returns:
            str or None: "create", "cancel", or None if nothing was clicked.
        """
        if self.create_rect.collidepoint(pos):
            return "create"
        elif self.cancel_rect.collidepoint(pos):
            return "cancel"
        return None

    def handle_key_input(self, event: pygame.event.Event, deck_container: DeckContainer) -> Optional[str]:
        """
        Process keyboard input when the add window is active.

        Args:
            event (pygame.event.Event): The keyboard event.
            deck_container (DeckContainer): Reference to the deck container (for name checking & creation).

        Returns:
            str or None: If a valid deck was created, returns the deck name. If canceled, returns "cancel". Else None.
        """
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]

        elif event.unicode.isprintable() and len(self.text) < 25:
            self.text += event.unicode

        elif event.key == pygame.K_RETURN:
            name = self.text.strip()
            if name and deck_container.name_available(name):
                deck_container.add_deck(name)
                return name
            else:
                self.name_accepted = False

        elif event.key == pygame.K_ESCAPE:
            return "cancel"

        return None


