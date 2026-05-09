# =============================================================
# main.py - Student 1
# Entry point: starts the game launcher
# =============================================================

import pygame
import sys

from menu import show_menu
from mode_select import show_mode_select
from table_tennis import run_table_tennis
from penalty_kicks import run_penalty_kicks
from pool_game import run_pool
from red_hands import run_red_hands
from score_screen import show_winner


def main():
    # Initialise Pygame and create the window
    pygame.init()

    SCREEN_W = 900
    SCREEN_H = 600
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("2 Player Games - The Challenge")

    clock = pygame.time.Clock()

    # Main loop: keeps returning to menu after each game
    while True:

        # Step 1: Show game selection menu (Student 2's file)
        game_choice = show_menu(screen, clock)

        # If player clicked Quit
        if game_choice == "quit":
            pygame.quit()
            sys.exit()

        # Step 2: Show mode selection (Student 3's file)
        mode_choice = show_mode_select(screen, clock)

        # If player pressed Back
        if mode_choice == "back":
            continue  # Go back to menu

        # True = single player vs AI, False = two players
        single_player = (mode_choice == "single")

        # Step 3: Launch the chosen game
        winner = None

        if game_choice == "table_tennis":
            winner = run_table_tennis(screen, clock, single_player)

        elif game_choice == "penalty_kicks":
            winner = run_penalty_kicks(screen, clock, single_player)

        elif game_choice == "pool":
            winner = run_pool(screen, clock, single_player)

        elif game_choice == "red_hands":
            winner = run_red_hands(screen, clock, single_player)

        else:
            continue  # Unknown choice, loop back

        # Step 4: Show winner screen (Student 4's file)
        show_winner(screen, clock, winner)


# Python entry point
if __name__ == "__main__":
    main()