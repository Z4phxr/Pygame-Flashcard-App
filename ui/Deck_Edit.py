import pygame
from core.Card import Card
from resources.Images.Images import IMAGES
from core.Settings import *
from core.utils import wrap_text

class DeckEdit:
    """
    A GUI-based editor for managing a flashcard deck.
    Allows adding, editing, deleting, searching, and displaying cards.
    """

    def __init__(self, deck, panel_width=372, panel_margin=93):
        self.deck = deck
        self.cards_filtered = list(deck.cards)
        self.selected_index = None
        self.scroll_offset = 0
        self.max_scroll = 0

        self.title_font = pygame.font.Font(font_path, 36)
        self.search_font = pygame.font.Font(font_path, 24)
        self.card_font = pygame.font.Font(font_path, 24)

        self.search_text = ""
        self.searching = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.adding_card = False
        self.editing_card = False

        sw, sh = pygame.display.get_surface().get_size()
        self.left_rect = pygame.Rect(panel_margin, panel_margin, panel_width, sh - 2 * panel_margin)

        title_surf = self.title_font.render(deck.name, True, (50, 0, 30))
        title_r = title_surf.get_rect(center=(
            self.left_rect.centerx,
            self.left_rect.y + 30 + title_surf.get_height() // 2
        ))

        m = 12
        h_search = 40
        self.search_rect = pygame.Rect(
            self.left_rect.x + m,
            title_r.bottom + m,
            self.left_rect.width - 2 * m,
            h_search
        )

        self.card_rects = []
        self.clicked_front = False
        self.clicked_back = False
        self.front_scroll = 0
        self.back_scroll = 0

        # Input rectangles and buttons
        self.deck_edit_plus_rect = pygame.rect.Rect(670, 170, 140, 140)
        self.x_adding_rect = pygame.rect.Rect(872, 605, 40, 40)
        self.x_editing_rect  = pygame.rect.Rect(915, 595, 42, 42)
        self.front_input_rect = pygame.rect.Rect(605, 140, 300, 150)
        self.back_input_rect = pygame.rect.Rect(605, 384, 300, 150)
        self.delete_card_rect = pygame.rect.Rect(560, 597, 160, 42)
        self.save_changes_rect = pygame.rect.Rect(742, 597, 160, 42)
        self.create_card_rect = pygame.rect.Rect(622, 597, 220, 53)

        self.text_front = ""
        self.text_back = ""
        self.cursor_front_visible = False
        self.cursor_back_visible = False

        self.clicked_title = False
        self.text_title = deck.name
        self.title_input_rect = None

    def draw(self, screen: pygame.Surface) -> None:
        """
        Renders the current state of the deck editor to the screen,
        depending on the mode (editing, adding, or browsing).
        """
        if self.adding_card:
            screen.blit(IMAGES["DECK_ADD"], (0, 0))
            self._draw_text_only(
                screen,
                self.front_input_rect,
                self.text_front + ('|' if self.cursor_front_visible else ''),
                scroll=self.front_scroll
            )
            self._draw_text_only(
                screen,
                self.back_input_rect,
                self.text_back + ('|' if self.cursor_back_visible else ''),
                scroll=self.back_scroll
            )

        elif self.editing_card:
            screen.blit(IMAGES["DECK_SAVE"], (0, 0))
            if self.selected_index is not None:
                self._draw_text_only(
                    screen,
                    self.front_input_rect,
                    self.text_front + ('|' if self.cursor_front_visible else ''),
                    scroll=self.front_scroll
                )
                self._draw_text_only(
                    screen,
                    self.back_input_rect,
                    self.text_back + ('|' if self.cursor_back_visible else ''),
                    scroll=self.back_scroll
                )

        else:
            screen.blit(IMAGES["DECK_EDIT"], (0, 0))

        self._draw_left(screen)


    def handle_scroll(self, event: pygame.event.Event) -> None:
        """
        Handles mouse wheel scrolling events.

        Scrolls the front or back text editor when in editing mode,
        or scrolls the card list otherwise.

        Args:
            event (pygame.event.Event): The scroll event (mouse wheel).
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button not in (4, 5):
            return

        delta = 20 if event.button == 4 else -20

        if self.clicked_front:
            self.front_scroll = max(self.front_scroll + delta, 0)
            return

        if self.clicked_back:
            self.back_scroll = max(self.back_scroll + delta, 0)
            return

        self.scroll_offset = min(max(self.scroll_offset + delta, -self.max_scroll), 0)

    def handle_text_input(self, event: pygame.event.Event) -> None:
        """
        Handles text input based on the current focus context.

        This includes:
        - Deck title editing
        - Card search bar
        - Front and back text fields for card creation/editing

        Args:
            event (pygame.event.Event): The key press/input event.
        """
        # Deck title editing
        if self.clicked_title:
            if event.key == pygame.K_BACKSPACE:
                self.text_title = self.text_title[:-1]
            elif event.key == pygame.K_RETURN:
                self.deck.name = self.text_title
                self.clicked_title = False
                self.deck.save_deck()
            elif event.unicode and event.unicode.isprintable():
                self.text_title += event.unicode

            self.cursor_visible = True
            self.cursor_timer = 0
            return

        # Search bar input
        if self.searching:
            if event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
            elif event.unicode.isprintable() and len(self.search_text) < 25:
                self.search_text += event.unicode

            term = self.search_text.lower()
            self.cards_filtered = [c for c in self.deck.cards if term in c.front.lower()]
            self.scroll_offset = 0
            self.selected_index = None

        # Editing front text
        elif self.clicked_front:
            self._ensure_caret_visible(self.text_front, self.front_input_rect, 'front_scroll')

            if event.key == pygame.K_BACKSPACE:
                self.text_front = self.text_front[:-1]
            elif event.key == pygame.K_RETURN:
                self.text_front += "\n"
            elif event.unicode.isprintable():
                self.text_front += event.unicode

        # Editing back text
        elif self.clicked_back:
            self._ensure_caret_visible(self.text_back, self.back_input_rect, 'back_scroll')

            if event.key == pygame.K_BACKSPACE:
                self.text_back = self.text_back[:-1]
            elif event.key == pygame.K_RETURN:
                self.text_back += "\n"
            elif event.unicode.isprintable():
                self.text_back += event.unicode

        self.cursor_visible = True
        self.cursor_timer = 0

    def update_cursor(self, dt: int) -> None:
        """
        Updates cursor blink visibility based on elapsed time.
        """
        self.cursor_timer += dt
        if self.cursor_timer < 500:
            return

        if self.searching:
            self.cursor_visible = not self.cursor_visible
        if self.clicked_front:
            self.cursor_front_visible = not self.cursor_front_visible
        if self.clicked_back:
            self.cursor_back_visible = not self.cursor_back_visible

        self.cursor_timer = 0

    def handle_click(self, pos: tuple[int, int]) -> tuple[str, None] | None | tuple[str, int]:
        """
        Handles mouse click events and updates the UI state accordingly.
        """

        self.cursor_visible = False
        self.cursor_front_visible = False
        self.cursor_back_visible = False

        # Title input field
        if self.title_input_rect and self.title_input_rect.collidepoint(pos):
            self.clicked_title = True
            self.searching = self.adding_card = self.editing_card = False
            self.clicked_front = self.clicked_back = False
            self.cursor_visible = True
            self.cursor_timer = 0
            return 'edit_title', None

        # Search bar
        if self.search_rect.collidepoint(pos):
            self.searching = True
            self.selected_index = None
            self.adding_card = self.editing_card = False
            self.clicked_front = self.clicked_back = False
            return 'search', None

        # "+" icon to add a card
        if not (self.adding_card or self.editing_card) and self.deck_edit_plus_rect.collidepoint(pos):
            self.adding_card = True
            self.selected_index = None
            self.clicked_front = self.clicked_back = False
            self.text_front = self.text_back = ""
            return

        # Cancel add
        if self.adding_card:
            if self.x_adding_rect.collidepoint(pos):
                self.adding_card = False
                self.clicked_front = self.clicked_back = False
                return
            elif self.create_card_rect.collidepoint(pos):
                new_card = Card(self.text_front, self.text_back)
                self.deck.add_card(new_card)
                self.adding_card = False
                self.cards_filtered = list(self.deck.cards)

        # Front/back field clicks
        if self.editing_card or self.adding_card:
            if self.front_input_rect.collidepoint(pos):
                self.clicked_front, self.clicked_back = True, False
                self.cursor_front_visible = True
                self.searching = False
                return 'edit_front', None
            if self.back_input_rect.collidepoint(pos):
                self.clicked_front, self.clicked_back = False, True
                self.cursor_back_visible = True
                self.searching = False
                return 'edit_back', None

        # Editing: cancel / delete / save
        if self.editing_card:
            if self.x_editing_rect.collidepoint(pos):
                self.editing_card = False
                self.clicked_front = self.clicked_back = False
                return
            if self.delete_card_rect.collidepoint(pos):
                self.deck.delete_card(self.selected_index)
                self.cards_filtered = list(self.deck.cards)
                self.selected_index = None
                self.editing_card = False
                self.clicked_front = self.clicked_back = False
                return
            if self.save_changes_rect.collidepoint(pos):
                c = self.deck.cards[self.selected_index]
                c[2].front = self.text_front
                c[2].back = self.text_back
                if self.searching:
                    term = self.search_text.lower()
                    self.cards_filtered = [c for c in self.deck.cards if term in c[2].front.lower()]
                else:
                    self.cards_filtered = list(self.deck.cards)
                self.editing_card = False
                self.clicked_front = self.clicked_back = False
                return

        # Selecting a card
        for i, r in enumerate(self.card_rects):
            if r.collidepoint(pos):
                self.searching = False
                self.selected_index = i
                self.editing_card = True
                self.adding_card = False
                self.text_front = self.deck.cards[i][2].front
                self.text_back = self.deck.cards[i][2].back
                self.clicked_front = self.clicked_back = False
                return 'card', i

        # Click outside panel
        if not self.left_rect.collidepoint(pos):
            self.searching = False
            self.selected_index = None
            self.clicked_front = self.clicked_back = False

        return None

    def _draw_left(self, screen: pygame.Surface) -> None:
        """
        Draws the left-side panel with deck title, search bar,
        and list of cards.
        """
        title_color = (50, 0, 30)

        # Draw editable title field or static label
        if self.clicked_title:
            pygame.draw.rect(screen, (255, 255, 255), self.title_input_rect, border_radius=6)
            pygame.draw.rect(screen, (200, 150, 150), self.title_input_rect, 2, border_radius=6)
            disp = self.text_title + ('|' if self.cursor_visible else '')
            surf = self.title_font.render(disp, True, title_color)
            screen.blit(
                surf,
                (
                    self.title_input_rect.x + 8,
                    self.title_input_rect.y + (self.title_input_rect.height - surf.get_height()) // 2
                )
            )
        else:
            title_surface = self.title_font.render(self.text_title, True, title_color)
            title_rect = title_surface.get_rect(center=(
                self.left_rect.centerx,
                self.left_rect.y + title_surface.get_height() // 2 + 10
            ))
            screen.blit(title_surface, title_rect)
            self.title_input_rect = title_rect.inflate(16, 8)

        # Draw search box
        border_color = (200, 150, 150)
        pygame.draw.rect(screen, (255, 255, 255), self.search_rect, border_radius=6)
        pygame.draw.rect(screen, border_color, self.search_rect, 2, border_radius=6)

        display_text = self.search_text + '|' if self.searching and self.cursor_visible else self.search_text
        search_surface = self.search_font.render(display_text, True, (0, 0, 0))
        screen.blit(
            search_surface,
            (
                self.search_rect.x + 8,
                self.search_rect.y + (self.search_rect.height - search_surface.get_height()) // 2
            )
        )

        # Draw card list
        margin = 12
        y_start = self.search_rect.bottom + margin
        list_rect = pygame.Rect(
            self.left_rect.x + margin,
            y_start,
            self.left_rect.width - 2 * margin,
            self.left_rect.bottom - margin - y_start
        )

        view = pygame.Surface(list_rect.size, pygame.SRCALPHA)
        self.card_rects.clear()

        entry_height = self.card_font.get_height() + 16
        total_height = len(self.cards_filtered) * entry_height + 8
        self.max_scroll = max(0, total_height - list_rect.height)

        y = self.scroll_offset
        for i, card in enumerate(self.cards_filtered):
            selected = (i == self.selected_index)
            bg_color = (219, 161, 156) if selected else (255, 221, 210)

            entry_rect = pygame.Rect(0, y, list_rect.width, entry_height - 4)
            pygame.draw.rect(view, bg_color, entry_rect, border_radius=4)

            text_surface = self.card_font.render(card[2].front, True, (20, 20, 20))
            view.blit(text_surface, (8, y + 4))

            self.card_rects.append(pygame.Rect(
                list_rect.x,
                list_rect.y + y,
                list_rect.width,
                entry_height
            ))

            y += entry_height

        screen.blit(view, list_rect.topleft)

    def _draw_text_only(self, screen, rect: pygame.Rect, text: str, scroll: int) -> None:
        """
        Renders multi-line text inside a given rectangle with scroll offset.
        """
        prev_clip = screen.get_clip()
        screen.set_clip(rect)

        lines = wrap_text(text, self.card_font, rect.width)
        line_h = self.card_font.get_height()
        y0 = rect.y - scroll

        for ln in lines:
            if y0 + line_h < rect.y:
                y0 += line_h
                continue
            if y0 > rect.y + rect.height:
                break
            surf = self.card_font.render(ln, True, (20, 20, 20))
            screen.blit(surf, (rect.x, y0))
            y0 += line_h

        screen.set_clip(prev_clip)

    def _ensure_caret_visible(self, text: str, rect: pygame.Rect, scroll_attr: str) -> None:
        """
        Adjusts scroll to ensure the caret (last line) is visible within the text area.
        """
        lines = wrap_text(text, self.card_font, rect.width)
        line_h = self.card_font.get_height()
        caret_line = len(lines) - 1
        caret_y = caret_line * line_h

        scroll = getattr(self, scroll_attr)
        if caret_y - scroll > rect.height - line_h:
            scroll = caret_y - (rect.height - line_h)
        if caret_y - scroll < 0:
            scroll = caret_y
        setattr(self, scroll_attr, scroll)
