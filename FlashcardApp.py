import sys
import pygame

from core.Settings import *
from ui.States.States import MainMenuState
from resources.Images.Images import load_images


class FlashcardApp:
    """
    Main application class responsible for initializing Pygame,
    handling game states, and running the main loop.
    """

    def __init__(self):
        self.init_pygame()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Girly anki")

        try:
            load_images()
        except Exception as e:
            print(f"Error while loading images: {e}")
            pygame.quit()
            sys.exit()

        self.clock = pygame.time.Clock()
        self.current_state = MainMenuState(self)

    @staticmethod
    def init_pygame():
        """
        Initialize Pygame and set keyboard repeat delay.
        """
        pygame.init()
        pygame.key.set_repeat(300, 50)

    def change_state(self, new_state):
        """
        Change the current active program state.

        Args:
            new_state: An instance of a class that inherits from ProgramState.
        """
        self.current_state = new_state

    def run(self):
        """
        Run the main loop: handle events, update state, and render frames.
        """
        running = True
        while running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                self.current_state.handle_input(event)

            self.current_state.update(keys)
            self.current_state.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
