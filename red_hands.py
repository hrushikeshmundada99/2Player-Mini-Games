# =============================================================
# red_hands.py - Student 4 (UPGRADED)
# DIFFICULTY: EASY (2/5)
# Red Hands - Reaction / Reflex game
# =============================================================
import pygame
import random
import math
import time

def run_red_hands(screen, clock, single=False):
    """
    Run the Red Hands reflex game with visual 'juice'.
    """
    W, H = screen.get_size()
    # Create a secondary surface for screen shake effects
    display_surface = pygame.Surface((W, H))

    # ■■ Colors ■■
    DARK = (20, 20, 35)
    RED = (255, 50, 80)
    CYAN = (0, 255, 255)
    WHITE = (255, 255, 255)
    GREEN = (50, 255, 100)
    YELLOW = (255, 215, 0)
    ORANGE = (255, 140, 0)
    GRAY = (100, 100, 120)
    
    # ■■ Fonts ■■
    font_huge = pygame.font.SysFont("Impact", 100)
    font_big = pygame.font.SysFont("Impact", 60)
    font_med = pygame.font.SysFont("Arial", 32, bold=True)
    font_small = pygame.font.SysFont("Arial", 20, bold=True)

    # ■■ Game settings ■■
    TOTAL_ROUNDS = 5
    ai_base_min = 0.15
    ai_base_max = 0.70

    score_p1 = 0
    score_p2 = 0
    
    # Particle system list: [x, y, vx, vy, radius, color, lifetime]
    particles = []

    def spawn_particles(x, y, color, count=30):
        for _ in range(count):
            vx = random.uniform(-8, 8)
            vy = random.uniform(-8, 8)
            radius = random.randint(4, 10)
            lifetime = random.randint(30, 60)
            particles.append([x, y, vx, vy, radius, color, lifetime])

    def update_and_draw_particles(surf):
        for p in particles[:]:
            p[0] += p[2] # Update X
            p[1] += p[3] # Update Y
            p[3] += 0.2  # Add gravity
            p[4] -= 0.1  # Shrink radius
            p[6] -= 1    # Decrease lifetime
            
            if p[6] <= 0 or p[4] <= 0:
                particles.remove(p)
            else:
                pygame.draw.circle(surf, p[5], (int(p[0]), int(p[1])), int(p[4]))

    # ■■ Play each round ■■
    for round_num in range(1, TOTAL_ROUNDS + 1):
        # Progressive AI difficulty
        current_ai_max = max(0.25, ai_base_max - (round_num * 0.08))
        
        countdown_start = pygame.time.get_ticks()
        extra_wait_ms = random.randint(800, 2500)
        
        signal_shown = False
        signal_show_time = None
        ai_will_press_at = None
        round_result = None
        phase = "countdown"
        
        shake_frames = 0
        flash_color = None

        while round_result is None:
            clock.tick(60)
            now = pygame.time.get_ticks()
            
            # ■■ Events ■■
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "Draw"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "Draw"
                    
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        player_pressed = "p1" if event.key == pygame.K_SPACE else "p2"
                        shake_frames = 15 # Trigger screen shake
                        
                        if not signal_shown:
                            round_result = "early_p1" if player_pressed == "p1" else "early_p2"
                            flash_color = RED
                            spawn_particles(W//4 if player_pressed=="p1" else 3*W//4, H//2, RED, 50)
                        else:
                            round_result = player_pressed
                            flash_color = WHITE
                            spawn_particles(W//4 if player_pressed=="p1" else 3*W//4, H//2, GREEN, 50)

            # ■■ Logic ■■
            elapsed = now - countdown_start
            
            if phase == "countdown":
                if elapsed >= 3000:
                    phase = "waiting"
                    signal_show_time = now + extra_wait_ms
            elif phase == "waiting":
                if now >= signal_show_time and not signal_shown:
                    signal_shown = True
                    phase = "signal"
                    if single:
                        ai_react_secs = random.uniform(ai_base_min, current_ai_max)
                        ai_will_press_at = now + int(ai_react_secs * 1000)
            elif phase == "signal":
                if single and ai_will_press_at and now >= ai_will_press_at:
                    if round_result is None:
                        round_result = "p2"
                        shake_frames = 15
                        spawn_particles(3*W//4, H//2, CYAN, 50)
                    ai_will_press_at = None

            # ■■ Drawing to display_surface ■■
            display_surface.fill(DARK)
            
            # Background flash effect
            if flash_color:
                display_surface.fill(flash_color)
                flash_color = None # Flash only lasts one frame

            # Divider
            pygame.draw.line(display_surface, GRAY, (W // 2, 80), (W // 2, H - 60), 4)

            # Scores
            score_text = font_med.render(f"ROUND {round_num}/{TOTAL_ROUNDS}   |   P1: {score_p1}   |   {'AI' if single else 'P2'}: {score_p2}", True, WHITE)
            display_surface.blit(score_text, (W // 2 - score_text.get_width() // 2, 20))

            # Player 1 Zone
            p1_zone = font_med.render("PLAYER 1", True, RED)
            display_surface.blit(p1_zone, (W // 4 - p1_zone.get_width() // 2, H // 2 - 100))
            key1 = font_small.render("[ SPACEBAR ]", True, WHITE)
            display_surface.blit(key1, (W // 4 - key1.get_width() // 2, H // 2 - 60))

            # Player 2 Zone
            p2_label = "COMPUTER" if single else "PLAYER 2"
            p2_zone = font_med.render(p2_label, True, CYAN)
            display_surface.blit(p2_zone, (3 * W // 4 - p2_zone.get_width() // 2, H // 2 - 100))
            if not single:
                key2 = font_small.render("[ ENTER ]", True, WHITE)
                display_surface.blit(key2, (3 * W // 4 - key2.get_width() // 2, H // 2 - 60))

            # Center UI
            if phase == "countdown":
                secs_left = 3 - elapsed // 1000
                count_num = max(1, min(3, secs_left + 1))
                c_color = [ORANGE, YELLOW, GREEN][count_num - 1]
                count_text = font_huge.render(str(count_num), True, c_color)
                display_surface.blit(count_text, (W // 2 - count_text.get_width() // 2, H // 2 - 20))
            
            elif phase == "waiting":
                dots = font_big.render("WAIT...", True, GRAY)
                display_surface.blit(dots, (W // 2 - dots.get_width() // 2, H // 2 - 20))
            
            elif phase == "signal":
                # Pulsating effect using sine wave
                scale = 1.0 + 0.1 * math.sin(now / 50.0)
                pulsing_font = pygame.font.SysFont("Impact", int(80 * scale))
                hit = pulsing_font.render("HIT NOW!", True, GREEN)
                display_surface.blit(hit, (W // 2 - hit.get_width() // 2, H // 2 - hit.get_height() // 2 + 30))

            update_and_draw_particles(display_surface)

            # ■■ Screen Shake Application ■■
            shake_x, shake_y = 0, 0
            if shake_frames > 0:
                shake_x = random.randint(-8, 8)
                shake_y = random.randint(-8, 8)
                shake_frames -= 1

            screen.fill((0, 0, 0)) # Clear master screen
            screen.blit(display_surface, (shake_x, shake_y))
            pygame.display.flip()

        # ■■ Process Round Result ■■
        if round_result == "p1":
            score_p1 += 1
            msg = "PLAYER 1 WINS!"
            msg_color = RED
        elif round_result == "p2":
            score_p2 += 1
            msg = "COMPUTER WINS!" if single else "PLAYER 2 WINS!"
            msg_color = CYAN
        elif round_result == "early_p1":
            score_p2 += 1
            msg = "P1 TOO EARLY! Point P2."
            msg_color = ORANGE
        else:
            score_p1 += 1
            msg = "P2 TOO EARLY! Point P1."
            msg_color = ORANGE

        # Show result for 2 seconds, keeping particles moving
        result_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - result_start < 2000:
            clock.tick(60)
            display_surface.fill(DARK)
            
            rt = font_huge.render(msg, True, msg_color)
            display_surface.blit(rt, (W // 2 - rt.get_width() // 2, H // 2 - rt.get_height() // 2))
            
            update_and_draw_particles(display_surface)
            screen.fill((0,0,0))
            screen.blit(display_surface, (0,0))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "Draw"

    # ■■ Final Winner ■■
    if score_p1 > score_p2:
        return "Player 1"
    elif score_p2 > score_p1:
        return "Computer" if single else "Player 2"
    return "Draw"