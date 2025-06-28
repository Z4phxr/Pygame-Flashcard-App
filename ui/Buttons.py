import pygame

# ──────────────────────────────────────────────────────────────
# UI GEOMETRY CONFIGURATION
# Centralized definitions of clickable UI rectangles (buttons, bars)
# for various screens and modes in the application.
# Used for collision detection and layout control.
# ──────────────────────────────────────────────────────────────

# MAIN MENU BUTTONS
menu_learn_rect = pygame.rect.Rect(300, 180, 417, 105)
menu_decks_rect = pygame.rect.Rect(300, 317, 417, 105)
menu_settings_rect = pygame.rect.Rect(300, 452, 417, 105)

# SETTINGS SCREEN
settings_menu_rect = pygame.rect.Rect(330, 570, 370, 100)

# DECK SCREEN CONTROLS
deck_menu_rect = pygame.rect.Rect(705, 600, 267, 70)
search_bar_rect = pygame.rect.Rect(270, 600, 400, 70)
add_deck_rect = pygame.rect.Rect(267, 19, 55, 55)
sort_rect = pygame.rect.Rect(172, 19, 55, 55)

# DECK EDIT SCREEN
deck_edit_menu_rect = pygame.rect.Rect(755, 30, 180, 50)
deck_edit_decks_rect = pygame.rect.Rect(560, 30, 180, 50)

# LEARNING CARD SCREEN
card_menu_rect = pygame.rect.Rect(523, 46, 177, 45)
card_decks_rect = pygame.rect.Rect(325, 46, 177, 45)

# FINISH SCREEN BUTTONS
finish_decks_rect = pygame.rect.Rect(356, 376, 305, 78)
finish_menu_rect = pygame.rect.Rect(356, 478, 305, 78)

# BUNNY :3
bunny_mask = [
    (0, 595), (10, 593), (2, 577), (7, 556), (24, 536), (48, 520), (75, 508),
    (89, 504), (110, 479), (141, 449), (172, 433), (200, 421), (235, 415),
    (260, 423), (272, 448), (269, 479), (246, 489), (201, 493), (154, 506),
    (130, 522), (145, 539), (185, 540), (242, 543), (255, 565), (250, 596),
    (246, 636), (238, 650), (197, 646), (177, 629), (173, 612), (179, 592),
    (169, 583), (162, 585), (155, 604), (139, 621), (133, 638), (117, 661),
    (96, 661), (87, 672), (89, 700), (0, 700)
]