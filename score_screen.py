# =============================================================
# score_screen.py - Student 4
# Animated winner announcement screen
# =============================================================

import pygame
import random
import math

def show_winner(screen, clock, winner):
    """
    Display who won with a nice animated screen.
    'winner' should be a string like 'Player 1', 'Player 2', 'Computer', or 'Draw'
    """
    W, H = screen.get_size()

    # Colors
    DARK = (26, 26, 46)
    GOLD = (255, 215, 0)
    WHITE = (255, 255, 255)
    SILVER = (180, 180, 180)

    # Fonts
    font_big = pygame.font.SysFont("Arial", 62, bold=True)
    font_med = pygame.font.SysFont("Arial", 34, bold=True)
    font_sml = pygame.font.SysFont("Arial", 17)

    # Create floating particles for celebration effect
    particles = []
    for _ in range(60):
        particles.append({
            "x": random.randint(0, W),
            "y": random.randint(-H, 0),  # Start above screen
            "vx": random.uniform(-1.5, 1.5),
            "vy": random.uniform(1, 3.5),
            "color": random.choice([
                (255, 215, 0), (233, 69, 96), (76, 201, 240),
                (255, 140, 0), (114, 9, 183)
            ]),
            "size": random.randint(4, 10),
        })

    start_time = pygame.time.get_ticks()

    while True:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return  # Go back to menu

        elapsed = (pygame.time.get_ticks() - start_time) / 1000.0

        # 2. Drawing Logic
        screen.fill(DARK)

        # Update and draw particles (falling confetti)
        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]

            # Reset particle to top when it falls off screen
            if p["y"] > H + 10:
                p["y"] = random.randint(-50, -10)
                p["x"] = random.randint(0, W)

            pygame.draw.rect(screen, p["color"], (int(p["x"]), int(p["y"]), p["size"], p["size"]))

        # Pulsing color for winner name (cycles through brightness)
        pulse = abs(math.sin(elapsed * 2.5))
        pulse_color = (
            int(200 + 55 * pulse),
            int(180 + 35 * pulse),
            0
        )

        # Render Text
        t1 = font_big.render("WINNER!", True, GOLD)
        t2 = font_med.render(winner, True, pulse_color)
        t3 = font_sml.render("Press any key or click to return to menu", True, SILVER)

        # Blit (Draw) Text to Screen
        screen.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 120))
        screen.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 - 30))
        screen.blit(t3, (W // 2 - t3.get_width() // 2, H // 2 + 90))

        # 3. Update Display
        pygame.display.flip()
        clock.tick(60)

    