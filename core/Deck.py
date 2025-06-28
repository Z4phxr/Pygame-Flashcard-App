import datetime
import os
import json
import heapq
import pygame
from typing import Optional, Union

from core.Card import Card
from core.Enums import CardStatus
from core.Settings import font_path


class Deck:
    """
    Represents a flashcard deck. Handles card management,
    scheduling, JSON persistence, and rendering logic.
    """

    def __init__(self, name: Optional[str] = None, path: Optional[str] = None) -> None:
        self.name: str = name
        self.date = datetime.datetime.today()
        self.cards: list[tuple[datetime.datetime, int, Card]] = []
        self.file_path = path
        self.last_practised: Optional[datetime.datetime] = None

        self.rect: Optional[pygame.Rect] = None
        self.edit_rect: Optional[pygame.Rect] = None
        self.delete_rect: Optional[pygame.Rect] = None
        self.options_rect: Optional[pygame.Rect] = None
        self.side = 0

        self.title_font = pygame.font.Font(font_path, 30)

        self.load_deck()

    def __str__(self) -> str:
        return f"DECK {self.name}"

    def load_deck(self) -> None:
        """Load deck data from JSON and initialize as a min-heap."""

        cards_list = []
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.name = data.get("name", self.name)
                    cards_list = [Card.from_dict(c) for c in data.get("cards", [])]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading deck from {self.file_path}: {e}")

        now = datetime.datetime.today()
        heap_items = []
        for card in cards_list:
            sd = card.scheduled_date
            if isinstance(sd, str):
                try:
                    sd = datetime.datetime.fromisoformat(sd)
                except ValueError:
                    sd = now
            if not isinstance(sd, datetime.datetime):
                sd = now
            card.scheduled_date = sd
            heap_items.append((sd, id(card), card))

        self.cards = heap_items
        heapq.heapify(self.cards)

    def add_card(self, card: Card) -> Card:
        """Add a card to the heap and save."""

        now = datetime.datetime.today()
        if isinstance(card.scheduled_date, str):
            try:
                card.scheduled_date = datetime.datetime.fromisoformat(card.scheduled_date)
            except ValueError:
                card.scheduled_date = now
        if not isinstance(card.scheduled_date, datetime.datetime):
            card.scheduled_date = now

        heapq.heappush(self.cards, (card.scheduled_date, id(card), card))
        self._save_cards_only()
        return card

    def delete_card(self, card_or_index: Union[int, Card]) -> Card:
        """Remove a card by index or instance and re-heapify."""

        if isinstance(card_or_index, int):
            if 0 <= card_or_index < len(self.cards):
                _, _, removed = self.cards.pop(card_or_index)
            else:
                raise IndexError(f"No card at index {card_or_index}")
        else:
            idx = next((i for i, (_, _, c) in enumerate(self.cards) if c is card_or_index), None)
            if idx is None:
                raise ValueError("Card not found in deck")
            _, _, removed = self.cards.pop(idx)

        heapq.heapify(self.cards)
        self._save_cards_only()
        return removed

    def reset_deck(self) -> None:
        """Reset all cards to initial learning state."""

        now = datetime.datetime.now()
        new_heap = []

        for _, _, card in self.cards:
            card.status = CardStatus.NEW
            card.repetition = 0
            card.interval = 0
            card.easiness = 2.5
            card.lapses = 0
            card.learning_index = 0
            card.last_review = None
            card.scheduled_date = now
            card.history = []
            new_heap.append((card.scheduled_date, id(card), card))

        self.cards = new_heap
        heapq.heapify(self.cards)
        self._save_cards_only()

    def save_deck(self) -> None:
        """Save full deck to JSON."""

        data = {
            "name": self.name,
            "cards": [c.to_dict() for _, _, c in self.cards]
        }
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving deck to {self.file_path}: {e}")

    def _save_cards_only(self) -> None:
        """Helper to save only cards (no name/metadata)."""

        data = {"cards": [c.to_dict() for _, _, c in self.cards]}
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving deck after change: {e}")

    def draw(self, surface: pygame.Surface, x: int, y: int, width: int = 216, height: int = 138) -> None:
        if self.side:
            self._draw_back(surface, x, y, width, height)
        else:
            self._draw_front(surface, x, y, width, height)

    def _draw_front(self, surface: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
        pygame.draw.rect(surface, (255, 249, 245), (x, y, width, height), border_radius=20)
        pygame.draw.rect(surface, (225, 146, 174), (x, y, width, height), 4, border_radius=20)

        text_surface = self.title_font.render(self.name, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(text_surface, text_rect)

        self.rect = pygame.Rect(x, y, width, height)

        circle_radius = 16
        circle_center = (x + width - circle_radius - 8, y + circle_radius + 4)
        pygame.draw.circle(surface, (255, 221, 210), circle_center, circle_radius)

        dots_font = pygame.font.Font(font_path, 22)
        dots_text = dots_font.render("...", True, (0, 0, 0))
        dots_rect = dots_text.get_rect(center=(circle_center[0], circle_center[1] - 8))
        surface.blit(dots_text, dots_rect)

        self.options_rect = pygame.Rect(0, 0, circle_radius * 2, circle_radius * 2)
        self.options_rect.center = circle_center

    def _draw_back(self, surface: pygame.Surface, x: int, y: int, width: int, height: int) -> None:
        pygame.draw.rect(surface, (255, 249, 245), (x, y, width, height), border_radius=20)
        pygame.draw.rect(surface, (225, 146, 174), (x, y, width, height), 4, border_radius=20)

        font_small = pygame.font.Font(font_path, 24)

        created_text = "Created: " + self.date.strftime("%Y-%m-%d")
        surface.blit(font_small.render(created_text, True, (50, 50, 50)), (x + 10, y + 10))

        last_text = "Last practised: "
        last_text += self.last_practised.strftime("%Y-%m-%d") if self.last_practised else "never"
        surface.blit(font_small.render(last_text, True, (50, 50, 50)), (x + 10, y + 35))

        progress = 50  # Static for now
        bar_width = width - 50
        bar_height = 15
        bar_x = x + 10
        bar_y = y + 65

        pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (100, 200, 100), (bar_x, bar_y, bar_width * (progress / 100), bar_height))
        surface.blit(font_small.render(f"{progress:.0f}%", True, (0, 0, 0)), (bar_x + bar_width + 5, bar_y - 2))

        self.edit_rect = pygame.Rect(x + 10, y + 95, 90, 30)
        pygame.draw.rect(surface, (180, 220, 250), self.edit_rect, border_radius=20)
        surface.blit(font_small.render("Edit", True, (0, 0, 0)), (self.edit_rect.x + 30, self.edit_rect.y))

        self.delete_rect = pygame.Rect(x + width - 100, y + 95, 90, 30)
        pygame.draw.rect(surface, (250, 150, 150), self.delete_rect, border_radius=20)
        surface.blit(font_small.render("Delete", True, (0, 0, 0)), (self.delete_rect.x + 30, self.delete_rect.y))

        self.rect = pygame.Rect(x, y, width, height)

        circle_radius = 16
        circle_center = (x + width - circle_radius - 8, y + circle_radius + 4)
        pygame.draw.circle(surface, (255, 221, 210), circle_center, circle_radius)

        dots_font = pygame.font.Font(font_path, 22)
        dots_text = dots_font.render("<-", True, (0, 0, 0))
        dots_rect = dots_text.get_rect(center=(circle_center[0], circle_center[1] - 2))
        surface.blit(dots_text, dots_rect)
