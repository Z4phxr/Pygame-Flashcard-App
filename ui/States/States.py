from core.utils import point_in_polygon
from ui.States.ABCProgramState import ProgramState
from resources.Images.Images import IMAGES
from ui.Buttons import *
from ui.Deck_container import DeckContainer
from ui.Delete_Window import DeleteWindow
from ui.Add_Window import AddDeckWindow
from ui.Deck_Edit import DeckEdit
from ui.LearningSession import LearningSession


class MainMenuState(ProgramState):
    """
    Main menu state of the application.
    Displays the main menu UI and allows transitions to other states.
    """

    def __init__(self, game):
        self.game = game

        # UI clickable areas
        self.learn_rect = menu_learn_rect
        self.deck_rect = menu_decks_rect
        self.settings_rect = menu_settings_rect

        # Bunny easter egg logic
        self.bunny = False
        self.bunny_activated_at = 0

        # Deck container initialized once here
        self.deck_container = DeckContainer()

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.learn_rect.collidepoint(event.pos):
                self.game.change_state(LearnState(self.game, self.deck_container))
            elif self.deck_rect.collidepoint(event.pos):
                self.game.change_state(DeckScreenState(self.game))
            elif self.settings_rect.collidepoint(event.pos):
                self.game.change_state(SettingsState(self.game))
            elif point_in_polygon(event.pos, bunny_mask):
                self.bunny = True
                self.bunny_activated_at = pygame.time.get_ticks()

    def update(self, keys):
        if self.bunny:
            now = pygame.time.get_ticks()
            if now - self.bunny_activated_at > 5000:
                self.bunny = False

    def draw(self, screen):
        if self.bunny:
            screen.blit(IMAGES["BUNNY_SMILE"], (0, 0))
        else:
            screen.blit(IMAGES["MAIN_MENU"], (0, 0))



class SettingsState(ProgramState):
    """
    Settings screen state.
    """

    def __init__(self, game):
        self.game = game
        self.menu_rect = settings_menu_rect

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_rect.collidepoint(event.pos):
                self.game.change_state(MainMenuState(self.game))

    def update(self, keys):
        pass

    def draw(self, screen):
        screen.blit(IMAGES["SETTINGS"], (0, 0))


class DeckScreenState(ProgramState):
    """
    Manages the deck selection screen, including deck rendering,
    user interaction (clicks, typing), and modal windows for
    creating or deleting decks.
    """

    def __init__(self, game):
        self.game = game
        self.menu_rect = deck_menu_rect
        self.search_bar_rect = search_bar_rect
        self.add_rect = add_deck_rect
        self.delete_window = None
        self.add_window = None
        self.deck_container = DeckContainer()

    def handle_input(self, event):
        # ─── SCROLL WHEEL ───────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            self.deck_container.handle_scroll(event)
            return

        # ─── LEFT CLICK ─────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.delete_window:
                if self.delete_window.no_rect.collidepoint((mx, my)):
                    self.delete_window = None
                    return
                elif self.delete_window.yes_rect.collidepoint((mx, my)):
                    self.deck_container.delete_deck(self.delete_window.deck_name)
                    self.delete_window = None
                    return

            if self.add_window:
                action = self.add_window.handle_click((mx, my))
                if action == "create":
                    name = self.add_window.text.strip()
                    if name and self.deck_container.name_available(name):
                        self.deck_container.add_deck(name)
                        self.add_window = None
                        deck = self.deck_container.get_deck(name)
                        self.game.change_state(DeckEditState(self.game, deck))
                    else:
                        self.add_window.name_accepted = False
                elif action == "cancel":
                    self.add_window = None
                return

            if self.menu_rect.collidepoint(mx, my):
                self.game.change_state(MainMenuState(self.game))
                return

            if self.add_rect.collidepoint(mx, my):
                self.add_window = AddDeckWindow()
                return

            result = self.deck_container.handle_click((mx, my))
            if result:
                match result["action"]:
                    case "edit":
                        self.game.change_state(DeckEditState(self.game, result["deck"]))
                    case "learn":
                        self.game.change_state(LearnState(self.game, result["deck"]))
                    case "delete":
                        self.delete_window = DeleteWindow(result["deck_name"])
                return
            else:
                self.deck_container.searching = False
                self.deck_container.cursor_visible = False
            return

        # ─── KEYBOARD INPUT ─────────────────────────────────────────────
        if event.type == pygame.KEYDOWN:
            if self.add_window:
                result = self.add_window.handle_key_input(event, self.deck_container)
                if result == "cancel":
                    self.add_window = None
                elif isinstance(result, str):
                    deck = self.deck_container.get_deck(result)
                    self.game.change_state(DeckEditState(self.game, deck))
                    self.add_window = None

            if self.deck_container.searching:
                self.deck_container.handle_search_input(event)
                return


    def update(self, keys):
        dt = self.game.clock.get_time()
        self.deck_container.update_cursor(dt)

    def draw(self, screen):
        screen.blit(IMAGES["DECKS"], (0, 0))
        self.deck_container.draw(screen)
        if self.delete_window:
            self.delete_window.draw(screen)
        elif self.add_window:
            self.add_window.draw(screen)



class DeckEditState(ProgramState):
    """
    State for editing an individual deck.
    Handles input, navigation, and delegates drawing and card logic to DeckEdit.
    """
    def __init__(self, game, deck):
        self.game = game
        self.deck = deck
        self.menu_rect = deck_edit_menu_rect
        self.decks_rect = deck_edit_decks_rect
        self.deck_edit = DeckEdit(self.deck)

    def handle_input(self, event):
        # ─── SCROLL WHEEL ───────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            self.deck_edit.handle_scroll(event)
            return

        # ─── LEFT CLICK ──────────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.menu_rect.collidepoint(mx, my):
                self.game.change_state(MainMenuState(self.game))
                return

            if self.decks_rect.collidepoint(mx, my):
                self.game.change_state(DeckScreenState(self.game))
                return

            result = self.deck_edit.handle_click((mx, my))
            if not result:
                self.deck_edit.searching = False
                self.deck_edit.clicked_front = False
                self.deck_edit.clicked_back = False
                self.deck_edit.clicked_title = False
                return

            kind, idx = result
            if kind == 'card':
                card = self.deck.cards[idx]
                print(f"Selected card #{idx}: {card[2].front}")
            return

        # ─── KEYBOARD INPUT ───────────────────────────────────────────────────
        if event.type == pygame.KEYDOWN:
            if (self.deck_edit.searching
                    or self.deck_edit.clicked_title
                    or self.deck_edit.clicked_front
                    or self.deck_edit.clicked_back):
                self.deck_edit.handle_text_input(event)
                return

    def update(self, keys):
        dt = self.game.clock.get_time()
        self.deck_edit.update_cursor(dt)

    def draw(self, screen):
        self.deck_edit.draw(screen)



class LearnState(ProgramState):
    """
    State for learning cards from a selected deck.
    Handles navigation and delegates logic to LearningSession.
    """
    def __init__(self, game, deck):
        self.game = game
        self.deck = deck
        self.menu_rect = card_menu_rect
        self.decks_rect = card_decks_rect
        self.session = LearningSession(self.deck)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_rect.collidepoint(event.pos):
                self.game.change_state(MainMenuState(self.game))
            elif self.decks_rect.collidepoint(event.pos):
                self.game.change_state(DeckScreenState(self.game))
            else:
                self.session.handle_click(event)

    def update(self, keys):
        if self.session.finish:
            self.game.change_state(FinishState(self.game))

    def draw(self, screen):
        self.session.draw(screen)



class FinishState(ProgramState):
    """
    State displayed after completing a learning session.
    Offers navigation to menu or deck screen.
    """
    def __init__(self, game):
        self.game = game
        self.menu_rect = finish_menu_rect
        self.decks_rect = finish_decks_rect

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.decks_rect.collidepoint(event.pos):
                self.game.change_state(DeckScreenState(self.game))
            elif self.menu_rect.collidepoint(event.pos):
                self.game.change_state(MainMenuState(self.game))

    def update(self, keys):
        pass

    def draw(self, screen):
        screen.blit(IMAGES["FINISH"], (0, 0))


