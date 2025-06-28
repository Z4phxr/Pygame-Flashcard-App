import pygame
from resources.Images.Images import IMAGES
from core.Subdeck import Subdeck
from core.Enums import Rating
from core.Scheduler import Scheduler
from core.Settings import *
from core.utils import draw_wrapped_text_centered


class LearningSession:
    """
    Handles the logic and UI for a single learning session using a Subdeck.
    Displays cards, tracks progress, and processes user input.
    """

    repeat_rect = pygame.Rect(105, 586, 180, 48)
    hard_rect = pygame.Rect(312, 586, 180, 48)
    medium_rect = pygame.Rect(515, 586, 180, 48)
    easy_rect = pygame.Rect(715, 586, 180, 48)

    action_buttons = [
        (repeat_rect, Rating.AGAIN),
        (hard_rect, Rating.HARD),
        (medium_rect, Rating.GOOD),
        (easy_rect, Rating.EASY),
    ]

    def __init__(self, deck) -> None:
        self.deck = deck  # Can be a Deck or a DeckContainer
        self.subdeck = Subdeck(self.deck, 20)
        self.current_card = self.subdeck.current_card
        self.side = 0  # 0 = front, 1 = back
        self.card_rect = pygame.Rect(164, 117, 673, 436)
        self.scroll_offset = 0
        self.card_font = pygame.font.Font(font_path, 35)
        self.finish = self.current_card is None
        self.scheduler = Scheduler()

    def handle_click(self, event: pygame.event.Event) -> None:
        """Process mouse click events (flip card or submit rating)."""
        pos = event.pos

        if self.card_rect.collidepoint(pos):
            self.side = not self.side
            return

        if self.side == 1:
            for rect, rating in self.action_buttons:
                if rect.collidepoint(pos):
                    self.subdeck.modify_card(rating)
                    self.current_card = self.subdeck.get_next_card()
                    self.side = 0
                    self.subdeck.save_deck()

                    if not self.current_card:
                        self.finish = True
                    return

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the current card side (front/back) and text."""
        if not self.finish:
            image = IMAGES["CARD_BACK"] if self.side else IMAGES["CARD_FRONT"]
            screen.blit(image, (0, 0))

            text = self.current_card.back if self.side else self.current_card.front
            draw_wrapped_text_centered(
                surface=screen,
                text=text,
                font=self.card_font,
                rect=self.card_rect,
                scroll=self.scroll_offset,
                color=(20, 20, 20),
            )