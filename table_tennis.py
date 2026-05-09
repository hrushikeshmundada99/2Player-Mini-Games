# =============================================================
# table_tennis.py - Student 1 - DIFFICULTY: EASY (2/5)
# ARCADE EDITION - Neon Table Tennis
# =============================================================
import pygame
import random
import math

def draw_glow_circle(screen, color, pos, radius, glow=10, alpha=80):
    """Draw a circle with a soft neon glow around it."""
    for i in range(glow, 0, -2):
        s = pygame.Surface((radius * 2 + i * 2, radius * 2 + i * 2), pygame.SRCALPHA)
        a = int(alpha * (i / glow) * 0.5)
        pygame.draw.circle(s, (*color, a), (radius + i, radius + i), radius + i)
        screen.blit(s, (pos[0] - radius - i, pos[1] - radius - i))
    pygame.draw.circle(screen, color, pos, radius)

def draw_glow_rect(screen, color, rect, radius=8, glow=10, alpha=80):
    """Draw a rounded rect with neon glow."""
    r = pygame.Rect(rect)
    for i in range(glow, 0, -2):
        s = pygame.Surface((r.width + i * 2, r.height + i * 2), pygame.SRCALPHA)
        a = int(alpha * (i / glow) * 0.5)
        pygame.draw.rect(s, (*color, a),
                         (0, 0, r.width + i * 2, r.height + i * 2),
                         border_radius=radius + i)
        screen.blit(s, (r.x - i, r.y - i))
    pygame.draw.rect(screen, color, r, border_radius=radius)

def draw_trail(screen, trail, color):
    """Draw fading ball trail."""
    for i, (tx, ty) in enumerate(trail):
        alpha = int(180 * (i / len(trail)))
        size  = max(2, int(10 * (i / len(trail))))
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (size, size), size)
        screen.blit(s, (tx - size, ty - size))

def run_table_tennis(screen, clock, single=False):
    """
    Run the Arcade Neon Table Tennis game.
    single=True  -> right paddle is AI
    single=False -> right paddle is Player 2
    Returns: 'Player 1', 'Player 2', 'Computer', or 'Draw'
    """
    W, H = screen.get_size()

    # ■■ Colors ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    BG_COLOR    = (5, 5, 18)
    GRID_COLOR  = (0, 40, 80)
    P1_COLOR    = (255, 60, 120)    # Hot pink
    P2_COLOR    = (0, 220, 255)     # Cyan
    BALL_COLOR  = (255, 255, 255)
    TRAIL_COLOR = (180, 180, 255)
    NET_COLOR   = (40, 40, 100)
    GOLD        = (255, 215, 0)

    # ■■ Game constants ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    WIN_SCORE    = 5
    PADDLE_W     = 14
    PADDLE_H     = 90
    BALL_RADIUS  = 11
    PADDLE_SPEED = 7
    BALL_SPEED   = 7
    AI_SPEED     = 5

    # ■■ Paddle positions ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    paddle1 = pygame.Rect(30, H // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
    paddle2 = pygame.Rect(W - 30 - PADDLE_W, H // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)

    # ■■ Ball ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    ball_x   = float(W // 2)
    ball_y   = float(H // 2)
    ball_dx  = BALL_SPEED * random.choice([-1, 1])
    ball_dy  = BALL_SPEED * random.choice([-1, 1])
    trail    = []

    # ■■ Scores ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    score1 = 0
    score2 = 0

    # ■■ Hit flash effect ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    flash_timer  = 0
    flash_color  = (255, 255, 255)

    # ■■ Background stars ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    stars = [(random.randint(0, W), random.randint(0, H),
              random.randint(1, 2), random.randint(40, 160))
             for _ in range(60)]

    # ■■ Fonts ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    font_score = pygame.font.SysFont("Consolas", 52, bold=True)
    font_small = pygame.font.SysFont("Consolas", 15)
    font_label = pygame.font.SysFont("Consolas", 13)

    tick = 0

    # ■■ Main game loop ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    while True:
        clock.tick(60)
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Draw"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "Draw"

        # ■■ Player 1 input ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= PADDLE_SPEED
        if keys[pygame.K_s] and paddle1.bottom < H:
            paddle1.y += PADDLE_SPEED

        # ■■ Player 2 / AI input ■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        if single:
            if paddle2.centery < ball_y - 5 and paddle2.bottom < H:
                paddle2.y += AI_SPEED
            elif paddle2.centery > ball_y + 5 and paddle2.top > 0:
                paddle2.y -= AI_SPEED
        else:
            if keys[pygame.K_UP]   and paddle2.top > 0:    paddle2.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and paddle2.bottom < H: paddle2.y += PADDLE_SPEED

        # ■■ Move ball + build trail ■■■■■■■■■■■■■■■■■■■■■■■■■
        ball_x += ball_dx
        ball_y += ball_dy
        trail.append((int(ball_x), int(ball_y)))
        if len(trail) > 14:
            trail.pop(0)

        # ■■ Wall bounce ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        if ball_y - BALL_RADIUS <= 0 or ball_y + BALL_RADIUS >= H:
            ball_dy *= -1

        # ■■ Paddle collision ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        ball_rect = pygame.Rect(
            ball_x - BALL_RADIUS, ball_y - BALL_RADIUS,
            BALL_RADIUS * 2, BALL_RADIUS * 2
        )
        if ball_rect.colliderect(paddle1) and ball_dx < 0:
            ball_dx  *= -1
            relative  = (ball_y - paddle1.centery) / (PADDLE_H / 2)
            ball_dy   = relative * BALL_SPEED
            flash_timer = 8
            flash_color = P1_COLOR

        if ball_rect.colliderect(paddle2) and ball_dx > 0:
            ball_dx  *= -1
            relative  = (ball_y - paddle2.centery) / (PADDLE_H / 2)
            ball_dy   = relative * BALL_SPEED
            flash_timer = 8
            flash_color = P2_COLOR

        # ■■ Scoring ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        # Ball goes off left edge → Player 2 scores
        # Ball respawns near Player 2's paddle, moving toward Player 1
        if ball_x < 0:
            score2 += 1
            trail.clear()

            # ── 2-second countdown before next serve ──
            for countdown in range(2, 0, -1):
                for _ in range(60):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return "Draw"
                    screen.fill(BG_COLOR)
                    draw_glow_rect(screen, P1_COLOR, paddle1, radius=6, glow=12, alpha=100)
                    draw_glow_rect(screen, P2_COLOR, paddle2, radius=6, glow=12, alpha=100)
                    s1_surf = font_score.render(str(score1), True, P1_COLOR)
                    s2_surf = font_score.render(str(score2), True, P2_COLOR)
                    screen.blit(s1_surf, (W // 4 - s1_surf.get_width() // 2, 16))
                    screen.blit(s2_surf, (3 * W // 4 - s2_surf.get_width() // 2, 16))
                    cd_font = pygame.font.SysFont("Consolas", 72, bold=True)
                    cd_surf = cd_font.render(str(countdown), True, P2_COLOR)
                    screen.blit(cd_surf, (W // 2 - cd_surf.get_width() // 2, H // 2 - 40))
                    lbl_font = pygame.font.SysFont("Consolas", 22, bold=True)
                    p2_name = "Computer" if single else "Player 2"
                    lbl_surf = lbl_font.render(f"{p2_name} scored!", True, P2_COLOR)
                    screen.blit(lbl_surf, (W // 2 - lbl_surf.get_width() // 2, H // 2 - 110))
                    pygame.display.flip()
                    clock.tick(60)

            ball_x = float(paddle2.x - BALL_RADIUS * 3)   # start near P2 paddle
            ball_y = float(paddle2.centery)
            ball_dx = -BALL_SPEED                          # serve toward P1
            ball_dy = BALL_SPEED * random.choice([-1, 1])

        # Ball goes off right edge → Player 1 scores
        # Ball respawns near Player 1's paddle, moving toward Player 2
        if ball_x > W:
            score1 += 1
            trail.clear()

            # ── 2-second countdown before next serve ──
            for countdown in range(2, 0, -1):
                for _ in range(60):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return "Draw"
                    screen.fill(BG_COLOR)
                    draw_glow_rect(screen, P1_COLOR, paddle1, radius=6, glow=12, alpha=100)
                    draw_glow_rect(screen, P2_COLOR, paddle2, radius=6, glow=12, alpha=100)
                    s1_surf = font_score.render(str(score1), True, P1_COLOR)
                    s2_surf = font_score.render(str(score2), True, P2_COLOR)
                    screen.blit(s1_surf, (W // 4 - s1_surf.get_width() // 2, 16))
                    screen.blit(s2_surf, (3 * W // 4 - s2_surf.get_width() // 2, 16))
                    cd_font = pygame.font.SysFont("Consolas", 72, bold=True)
                    cd_surf = cd_font.render(str(countdown), True, P1_COLOR)
                    screen.blit(cd_surf, (W // 2 - cd_surf.get_width() // 2, H // 2 - 40))
                    lbl_font = pygame.font.SysFont("Consolas", 22, bold=True)
                    lbl_surf = lbl_font.render("Player 1 scored!", True, P1_COLOR)
                    screen.blit(lbl_surf, (W // 2 - lbl_surf.get_width() // 2, H // 2 - 110))
                    pygame.display.flip()
                    clock.tick(60)

            ball_x = float(paddle1.right + BALL_RADIUS * 3)  # start near P1 paddle
            ball_y = float(paddle1.centery)
            ball_dx = BALL_SPEED                              # serve toward P2
            ball_dy = BALL_SPEED * random.choice([-1, 1])

        # ■■ Win check ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        if score1 >= WIN_SCORE:
            return "Player 1"
        if score2 >= WIN_SCORE:
            return "Computer" if single else "Player 2"

        # ■■■■■■■■■■■■■■■■■■ DRAWING ■■■■■■■■■■■■■■■■■■■■■■■■
        # Dark background
        screen.fill(BG_COLOR)

        # Background stars
        for sx, sy, sr, sa in stars:
            twinkle = int(sa * (0.6 + 0.4 * math.sin(tick * 0.03 + sx)))
            s = pygame.Surface((sr * 2, sr * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (180, 180, 255, twinkle), (sr, sr), sr)
            screen.blit(s, (sx - sr, sy - sr))

        # Background grid (faint court lines)
        for y in range(0, H, 60):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (W, y), 1)
        for x in range(0, W, 80):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, H), 1)

        # Center net (dashed, glowing)
        for y in range(0, H, 22):
            net_rect = pygame.Rect(W // 2 - 2, y, 4, 14)
            s = pygame.Surface((8, 14), pygame.SRCALPHA)
            pygame.draw.rect(s, (*NET_COLOR, 200), (0, 0, 8, 14), border_radius=2)
            screen.blit(s, (W // 2 - 4, y))
            pygame.draw.rect(screen, (60, 60, 160), net_rect, border_radius=2)

        # Flash effect on hit
        if flash_timer > 0:
            flash_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            flash_surf.fill((*flash_color, int(40 * flash_timer / 8)))
            screen.blit(flash_surf, (0, 0))
            flash_timer -= 1

        # Ball trail
        draw_trail(screen, trail, TRAIL_COLOR)

        # Ball glow
        draw_glow_circle(screen, BALL_COLOR, (int(ball_x), int(ball_y)),
                         BALL_RADIUS, glow=16, alpha=100)

        # Paddles with glow
        draw_glow_rect(screen, P1_COLOR, paddle1, radius=6, glow=12, alpha=100)
        draw_glow_rect(screen, P2_COLOR, paddle2, radius=6, glow=12, alpha=100)

        # Player labels above paddles
        p1_lbl = font_label.render("P1", True, P1_COLOR)
        screen.blit(p1_lbl, (paddle1.centerx - p1_lbl.get_width() // 2, paddle1.top - 18))
        p2_lbl_text = "AI" if single else "P2"
        p2_lbl = font_label.render(p2_lbl_text, True, P2_COLOR)
        screen.blit(p2_lbl, (paddle2.centerx - p2_lbl.get_width() // 2, paddle2.top - 18))

        # Scores with glow colour
        s1_surf = font_score.render(str(score1), True, P1_COLOR)
        s2_surf = font_score.render(str(score2), True, P2_COLOR)
        screen.blit(s1_surf, (W // 4 - s1_surf.get_width() // 2, 16))
        screen.blit(s2_surf, (3 * W // 4 - s2_surf.get_width() // 2, 16))

        # Divider dots between scores
        for i in range(WIN_SCORE):
            dot_x = W // 2 - (WIN_SCORE * 14) // 2 + i * 14 + 7
            filled1 = i < score1
            filled2 = i < score2
            c1 = P1_COLOR if filled1 else (40, 40, 60)
            c2 = P2_COLOR if filled2 else (40, 40, 60)
            pygame.draw.circle(screen, c1, (dot_x - 30, 22), 5)
            pygame.draw.circle(screen, c2, (dot_x + 30, 22), 5)

        # Controls hint
        if single:
            hint_str = "W/S  ←→  AI  |  ESC: Exit"
        else:
            hint_str = "W/S  ←  P1    P2  →  ↑/↓  |  ESC: Exit"
        hint_surf = font_small.render(hint_str, True, (60, 60, 100))
        screen.blit(hint_surf, (W // 2 - hint_surf.get_width() // 2, H - 24))

        pygame.display.flip()