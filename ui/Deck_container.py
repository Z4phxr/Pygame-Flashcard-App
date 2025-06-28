import os
import json
import datetime
import pygame

from core.Deck import Deck
from ui.Buttons import search_bar_rect, add_deck_rect
from core.Settings import *


class DeckContainer:
    """
    Manages all deck cards in the deck screen: rendering, sorting,
    searching, and user interaction with deck elements.
    """

    sort_labels = [
        "Sort A-Z",
        "Sort Z-A",
        "Date ascending",
        "Date descending",
        "Last practised (oldest)",
        "Last practised (newest)"
    ]

    def __init__(self):
        # Fonts
        self.font = pygame.font.Font(font_path, 40)
        self.search_font = pygame.font.Font(font_path, 50)
        self.sort_font = pygame.font.Font(font_path, 30)

        # UI positions and rectangles
        self.rect = pygame.Rect(161, 85, 678, 444)
        self.search_bar_rect = search_bar_rect
        self.add_deck_rect = add_deck_rect
        self.sort_button_rect = pygame.Rect(172, 19, 55, 55)

        self.menu_pos = (50, 88)
        self.option_height = 45
        self.option_width = 300
        self.menu_height = len(self.sort_labels) * self.option_height + 25
        self.sort_rect = pygame.Rect(
            self.menu_pos[0],
            self.menu_pos[1],
            self.option_width,
            self.menu_height
        )

        # Deck data
        self.decks = []
        self.filtered_decks = []
        self.deck_count = 0
        self.folder = os.path.join(os.getcwd(), "resources", "Decks")
        self.all_cards = []

        # Scroll
        self.viewport = None
        self.scroll_offset = 0
        self.max_scroll = 0
        self.gap_between = 15

        # Sorting
        self.sorting_window = False
        self.sort_option_rects = []
        self.order = 3  # Default: Date descending
        self.init_sort_option_rects()

        # Search
        self.search_text = ""
        self.searched_phrase = ""
        self.searching = False
        self.cursor_visible = False
        self.cursor_timer = 0

        # Load decks from disk
        self.load_all_decks()

    def draw(self, screen):
        """
        Render all visual elements inside the deck container,
        including deck cards, search bar text, and the sort menu.
        """

        deck_width = 216
        deck_height = 138
        decks_per_row = 3

        self.viewport = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        total_rows = (len(self.decks) + decks_per_row - 1) // decks_per_row
        content_height = total_rows * (deck_height + self.gap_between)
        self.max_scroll = max(0, content_height - self.rect.height)

        for i, deck in enumerate(self.filtered_decks):
            row = i // decks_per_row
            col = i % decks_per_row
            x = col * (deck_width + self.gap_between)
            y = row * (deck_height + self.gap_between) + self.scroll_offset

            # Skip decks outside the viewport
            if y + deck_height < 0 or y > self.rect.height:
                continue
            deck.draw(self.viewport, x, y, width=deck_width, height=deck_height)

        # Draw search text with optional blinking cursor
        display_text = self.search_text
        if self.searching and self.cursor_visible:
            display_text += "|"
        text_surface = self.search_font.render(display_text, True, (0, 0, 0))
        screen.blit(text_surface, (self.search_bar_rect.x + 15, self.search_bar_rect.y + 5))

        # Draw decks
        screen.blit(self.viewport, self.rect.topleft)

        # Draw sort window
        if self.sorting_window:
            pygame.draw.rect(screen, (255, 210, 230), self.sort_rect, border_radius=6)
            for i, rect in enumerate(self.sort_option_rects):
                label = self.font.render(self.sort_labels[i], True, (50, 0, 30))
                screen.blit(label, (rect.x + 15, rect.y + 12))

    def handle_click(self, pos):
        """
        Handle a single left mouse click on interactive elements
        like the sort button, search bar, or individual deck cards.
        """

        # Sort window logic
        if self.sorting_window:
            for i, rect in enumerate(self.sort_option_rects):
                if rect.collidepoint(pos):
                    self.order = i
                    self.order_by()
                    self.sorting_window = False
                    return None
            if not self.sort_rect.collidepoint(pos):
                self.sorting_window = False
            return None
        elif self.sort_button_rect.collidepoint(pos):
            self.sorting_window = not self.sorting_window
            return None

        # Search bar
        if self.search_bar_rect.collidepoint(pos):
            self.searching = True
            self.cursor_visible = True
            return None

        # Click outside
        self.searching = False
        self.cursor_visible = False

        # Deck click logic
        if not self.rect.collidepoint(pos):
            return None

        base_x, base_y = self.rect.topleft
        for deck in self.filtered_decks:
            if not hasattr(deck, "rect") or not hasattr(deck, "options_rect"):
                continue

            front_rect = deck.rect.move(base_x, base_y)
            options_rect = deck.options_rect.move(base_x, base_y)

            if options_rect.collidepoint(pos):
                deck.side = not deck.side
                return {"action": "toggle_card_side", "deck": deck}

            if front_rect.collidepoint(pos):
                if deck.side == 0:
                    return {"action": "learn", "deck": deck}
                else:
                    edit_rect = deck.edit_rect.move(base_x, base_y)
                    delete_rect = deck.delete_rect.move(base_x, base_y)
                    if edit_rect.collidepoint(pos):
                        return {"action": "edit", "deck": deck}
                    elif delete_rect.collidepoint(pos):
                        return {"action": "delete", "deck_name": deck.name}

        return None

    def handle_scroll(self, event):
        """
          Adjust the scroll offset when the user scrolls
          with the mouse wheel inside the deck container.
          """

        scroll_speed = 30
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_offset = min(self.scroll_offset + scroll_speed, 0)
            elif event.button == 5:
                self.scroll_offset = max(self.scroll_offset - scroll_speed, -self.max_scroll)

    def handle_search(self, phrase):
        """
        Filter the decks based on a search phrase and apply current sorting.
        """

        self.searched_phrase = phrase.lower()
        self.filtered_decks = [
            deck for deck in self.decks if self.searched_phrase in deck.name.lower()
        ]
        self.order_by()
        self.scroll_offset = 0

    def update_cursor(self, dt):
        """
         Update the blinking cursor in the search bar.
         """

        if self.searching:
            self.cursor_timer += dt
            if self.cursor_timer >= 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
        else:
            self.cursor_visible = False

    def init_sort_option_rects(self):
        """
          Precompute and store the rectangles representing
          clickable areas for each sort option.
          """

        self.sort_option_rects.clear()
        for i in range(len(self.sort_labels)):
            rect = pygame.Rect(
                self.menu_pos[0],
                self.menu_pos[1] + i * self.option_height,
                self.option_width,
                self.option_height
            )
            self.sort_option_rects.append(rect)

    def order_by(self):
        """
        Sort the filtered deck list based on the current sorting mode.
        Sorting is controlled by self.order.
        """

        key_map = {
            0: lambda d: d.name.lower(),
            1: lambda d: d.name.lower(),
            2: lambda d: d.date,
            3: lambda d: d.date,
            4: lambda d: d.last_practised or datetime.datetime.min,
            5: lambda d: d.last_practised or datetime.datetime.min
        }
        reverse_map = {1, 3, 5}
        self.filtered_decks = sorted(
            self.filtered_decks,
            key=key_map.get(self.order, lambda d: d.name),
            reverse=self.order in reverse_map
        )

    def load_all_decks(self):
        """
        Load all decks from JSON files in the deck folder.
        Updates the internal deck list and filtered list.
        """

        for filename in os.listdir(self.folder):
            if filename.endswith(".json"):
                path = os.path.join(self.folder, filename)
                name = os.path.splitext(filename)[0]
                deck = Deck(name, path)
                self.decks.append(deck)
                self.deck_count += 1
        self.filtered_decks = self.decks.copy()

    def delete_deck(self, name):
        """
        Delete a deck by name from memory and from disk.
        """

        self.decks = [d for d in self.decks if d.name != name]
        self.filtered_decks = [d for d in self.filtered_decks if d.name != name]
        self.deck_count = len(self.decks)

        file_path = os.path.join(self.folder, f"{name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

        self.scroll_offset = 0
        self.order_by()

    def add_deck(self, name):
        """
        Create a new deck and add it to the collection, if the name is available.
        """

        if any(deck.name == name for deck in self.decks):
            print(f"Deck '{name}' already exists.")
            return

        file_path = os.path.join(self.folder, f"{name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"cards": []}, f, indent=4)

        new_deck = Deck(name, file_path)
        self.decks.append(new_deck)
        self.filtered_decks.append(new_deck)
        self.deck_count += 1
        self.order_by()
        print(f"Added deck: {name}")

    def name_available(self, name: str) -> bool:
        """
        Check if a given deck name is available (case-insensitive, trimmed).
        """

        clean = name.strip().lower()
        return not any(clean == deck.name.strip().lower() for deck in self.decks)

    def get_deck(self, name):
        """
        Retrieve a deck object by its name.
        """

        clean = name.strip().lower()
        for deck in self.decks:
            if clean == deck.name.strip().lower():
                return deck
        raise ValueError(f"Deck '{name}' not found.")

    def handle_search_input(self, event: pygame.event.Event) -> None:
        """
        Handle keyboard input for typing in the search bar.
        """

        if event.key == pygame.K_BACKSPACE:
            self.search_text = self.search_text[:-1]
        elif event.unicode.isprintable() and len(self.search_text) < 25:
            self.search_text += event.unicode
        self.handle_search(self.search_text)
