# =============================================================
# penalty_kicks.py - Student 2 - DIFFICULTY: MEDIUM (3/5)
# ARCADE EDITION - Neon Stadium Penalty Kicks
# =============================================================
import pygame
import math
import random

def draw_glow_rect(screen, color, rect, radius=8, glow=10, alpha=80):
    r = pygame.Rect(rect)
    for i in range(glow, 0, -2):
        s = pygame.Surface((r.width + i * 2, r.height + i * 2), pygame.SRCALPHA)
        a = int(alpha * (i / glow) * 0.5)
        pygame.draw.rect(s, (*color, a),
                         (0, 0, r.width + i * 2, r.height + i * 2),
                         border_radius=radius + i)
        screen.blit(s, (r.x - i, r.y - i))
    pygame.draw.rect(screen, color, r, border_radius=radius)

def draw_glow_circle(screen, color, pos, radius, glow=10, alpha=80):
    for i in range(glow, 0, -2):
        s = pygame.Surface((radius * 2 + i * 2, radius * 2 + i * 2), pygame.SRCALPHA)
        a = int(alpha * (i / glow) * 0.5)
        pygame.draw.circle(s, (*color, a), (radius + i, radius + i), radius + i)
        screen.blit(s, (pos[0] - radius - i, pos[1] - radius - i))
    pygame.draw.circle(screen, color, pos, radius)

def draw_glow_line(screen, color, start, end, width=2, glow=6, alpha=80):
    for i in range(glow, 0, -2):
        s = pygame.Surface((abs(end[0]-start[0]) + i*2 + 20,
                            abs(end[1]-start[1]) + i*2 + 20), pygame.SRCALPHA)
        a = int(alpha * (i / glow) * 0.4)
        ox = min(start[0], end[0]) - i - 10
        oy = min(start[1], end[1]) - i - 10
        pygame.draw.line(s, (*color, a),
                         (start[0] - ox, start[1] - oy),
                         (end[0]   - ox, end[1]   - oy), width + i)
        screen.blit(s, (ox, oy))
    pygame.draw.line(screen, color, start, end, width)

def run_penalty_kicks(screen, clock, single=False):
    """
    Arcade Neon Penalty Kicks.
    single=True  -> AI goalkeeper
    single=False -> Player 2 controls goalkeeper
    Returns: 'Player 1', 'Player 2', 'Computer', or 'Draw'
    """
    W, H = screen.get_size()

    # ■■ Colors ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    BG          = (5, 12, 5)
    GRASS_DARK  = (0, 60, 10)
    GRASS_MID   = (0, 80, 15)
    NEON_WHITE  = (220, 255, 220)
    NET_COLOR   = (60, 180, 60)
    BALL_COL    = (255, 255, 255)
    P1_COL      = (255, 60, 120)
    GK_HUMAN    = (255, 215, 0)
    GK_AI       = (255, 120, 0)
    CYAN        = (0, 220, 255)
    GOLD        = (255, 215, 0)

    # ■■ Game settings ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    TOTAL_ROUNDS    = 5
    GK_SPEED        = 6
    AI_PATROL_SPEED = 3        # constant left-right patrol speed before shot
    BALL_SPEED      = 13
    AI_DELAY        = 22

    # ■■ Goal ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    GOAL_W  = 300
    GOAL_H  = 120
    goal_x  = W // 2 - GOAL_W // 2
    goal_y  = 60

    # ■■ Goalkeeper ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    GK_W = 50
    GK_H = 80
    gk = pygame.Rect(W // 2 - GK_W // 2, goal_y + GOAL_H - GK_H, GK_W, GK_H)

    BALL_START_X = W // 2
    BALL_START_Y = H - 120

    font_big   = pygame.font.SysFont("Consolas", 30, bold=True)
    font_med   = pygame.font.SysFont("Consolas", 22, bold=True)
    font_small = pygame.font.SysFont("Consolas", 15)

    goals_scored = 0
    saves_made   = 0
    tick         = 0

    # ■■ Patrol direction for AI goalkeeper ■■■■■■■■■■■■■■■■■■
    ai_patrol_dir = 1   # +1 = moving right, -1 = moving left

    # ■■ Crowd dots (background decoration) ■■■■■■■■■■■■■■■■■■
    crowd = [(random.randint(20, W-20),
              random.randint(H - 60, H - 10),
              random.choice([(255,60,120),(0,220,255),(255,215,0),(0,255,140)]),
              random.randint(3, 6))
             for _ in range(40)]

    # ■■ Round loop ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    for round_num in range(1, TOTAL_ROUNDS + 1):
        ball_x      = float(BALL_START_X)
        ball_y      = float(BALL_START_Y)
        direction   = None
        phase       = "aim"
        result_text = ""
        result_col  = GOLD
        gk.centerx  = W // 2

        ai_target_x    = W // 2
        ai_delay_count = 0
        round_running  = True

        ball_trail = []

        while round_running:
            clock.tick(60)
            tick += 1
            mx, my = pygame.mouse.get_pos()

            # ■■ Events ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "Draw"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "Draw"
                if event.type == pygame.MOUSEBUTTONDOWN and phase == "aim":
                    dx = mx - ball_x
                    dy = my - ball_y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        direction = [dx / dist * BALL_SPEED, dy / dist * BALL_SPEED]
                        phase = "shoot"
                        ai_target_x = ball_x + direction[0] * 40
                        ai_target_x = max(goal_x + GK_W // 2,
                                          min(goal_x + GOAL_W - GK_W // 2, ai_target_x))
                        ai_delay_count = AI_DELAY

            # ■■ GK movement ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            keys = pygame.key.get_pressed()
            if single:
                if phase == "aim":
                    # ── Constant patrol: bounce left and right across the goal ──
                    gk.x += AI_PATROL_SPEED * ai_patrol_dir

                    # Reverse direction at goal edges
                    if gk.right >= goal_x + GOAL_W:
                        gk.right = goal_x + GOAL_W
                        ai_patrol_dir = -1
                    elif gk.left <= goal_x:
                        gk.left = goal_x
                        ai_patrol_dir = 1

                elif phase == "shoot":
                    # ── React to shot after short delay ──
                    if ai_delay_count > 0:
                        ai_delay_count -= 1
                    else:
                        if gk.centerx < ai_target_x - 4:
                            gk.x += GK_SPEED + 1
                        elif gk.centerx > ai_target_x + 4:
                            gk.x -= GK_SPEED + 1
                    gk.x = max(goal_x, min(goal_x + GOAL_W - GK_W, gk.x))
            else:
                if keys[pygame.K_a] and gk.left > goal_x:
                    gk.x -= GK_SPEED
                if keys[pygame.K_d] and gk.right < goal_x + GOAL_W:
                    gk.x += GK_SPEED

            # ■■ Move ball ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            if phase == "shoot" and direction:
                ball_x += direction[0]
                ball_y += direction[1]
                ball_trail.append((int(ball_x), int(ball_y)))
                if len(ball_trail) > 12:
                    ball_trail.pop(0)

                ball_rect = pygame.Rect(ball_x - 15, ball_y - 15, 30, 30)
                goal_rect = pygame.Rect(goal_x, goal_y, GOAL_W, GOAL_H)

                if ball_rect.colliderect(gk):
                    result_text = "SAVED! 🧤"
                    result_col  = GK_AI if single else GK_HUMAN
                    saves_made += 1
                    phase = "result"
                elif ball_y < goal_y + GOAL_H and ball_rect.colliderect(goal_rect):
                    result_text = "⚽ GOAL!"
                    result_col  = CYAN
                    goals_scored += 1
                    phase = "result"
                elif ball_y < 0 or ball_x < 0 or ball_x > W:
                    result_text = "MISSED!"
                    result_col  = (200, 80, 80)
                    phase = "result"

            # ■■ Result pause ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            if phase == "result":
                screen.fill(BG)
                for glow_i in range(10, 0, -2):
                    gs = font_big.render(result_text, True,
                                         tuple(min(c + 60, 255) for c in result_col))
                    screen.blit(gs, (W // 2 - gs.get_width() // 2 + glow_i,
                                     H // 2 - 20 + glow_i))
                rt = font_big.render(result_text, True, result_col)
                screen.blit(rt, (W // 2 - rt.get_width() // 2, H // 2 - 20))
                sc = font_small.render(
                    f"Goals: {goals_scored}   Saves: {saves_made}", True, NEON_WHITE)
                screen.blit(sc, (W // 2 - sc.get_width() // 2, H // 2 + 30))
                pygame.display.flip()
                pygame.time.wait(1600)
                round_running = False
                continue

            # ■■■■■■■■■■■■■■■■ DRAWING ■■■■■■■■■■■■■■■■■■■■■■
            screen.fill(BG)

            # Striped grass
            stripe_w = W // 10
            for i in range(10):
                c = GRASS_DARK if i % 2 == 0 else GRASS_MID
                pygame.draw.rect(screen, c, (i * stripe_w, 0, stripe_w, H - 55))

            # Crowd in background
            for cx, cy, cc, cs in crowd:
                sway = int(3 * math.sin(tick * 0.04 + cx))
                pygame.draw.circle(screen, cc, (cx, cy + sway), cs)

            # Goal net lines
            for xi in range(goal_x, goal_x + GOAL_W, 20):
                pygame.draw.line(screen, (20, 80, 20),
                                 (xi, goal_y), (xi, goal_y + GOAL_H), 1)
            for yi in range(goal_y, goal_y + GOAL_H, 20):
                pygame.draw.line(screen, (20, 80, 20),
                                 (goal_x, yi), (goal_x + GOAL_W, yi), 1)

            # Goal posts with glow
            post_col = (200, 255, 200)
            draw_glow_rect(screen, post_col,
                           (goal_x - 7, goal_y, 7, GOAL_H + 7), radius=3, glow=8, alpha=60)
            draw_glow_rect(screen, post_col,
                           (goal_x + GOAL_W, goal_y, 7, GOAL_H + 7), radius=3, glow=8, alpha=60)
            draw_glow_rect(screen, post_col,
                           (goal_x - 7, goal_y - 7, GOAL_W + 14, 7), radius=3, glow=8, alpha=60)

            # Penalty spot
            draw_glow_circle(screen, NEON_WHITE,
                             (BALL_START_X, BALL_START_Y), 8, glow=6, alpha=60)

            # Center circle on pitch
            pygame.draw.circle(screen, (30, 100, 30),
                               (W // 2, H - 60), 80, 1)
            pygame.draw.line(screen, (30, 100, 30),
                             (0, H - 60), (W, H - 60), 1)

            # Ball trail
            for i, (tx, ty) in enumerate(ball_trail):
                alpha = int(150 * (i / max(1, len(ball_trail))))
                size  = max(2, int(14 * (i / max(1, len(ball_trail)))))
                ts = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(ts, (255, 255, 200, alpha), (size, size), size)
                screen.blit(ts, (tx - size, ty - size))

            # Ball
            draw_glow_circle(screen, BALL_COL,
                             (int(ball_x), int(ball_y)), 15, glow=10, alpha=80)
            pygame.draw.circle(screen, (40, 40, 40),
                               (int(ball_x), int(ball_y)), 15, 2)

            # Goalkeeper with glow
            gk_color = GK_AI if single else GK_HUMAN
            draw_glow_rect(screen, gk_color, gk, radius=8, glow=12, alpha=90)
            gk_lbl = font_small.render("AI" if single else "GK", True, (10, 10, 10))
            screen.blit(gk_lbl, (gk.centerx - gk_lbl.get_width() // 2,
                                  gk.centery - gk_lbl.get_height() // 2))

            # Aim guide line
            if phase == "aim":
                draw_glow_line(screen, GOLD,
                               (int(ball_x), int(ball_y)), (mx, my),
                               width=2, glow=6, alpha=80)
                pygame.draw.circle(screen, GOLD, (mx, my), 6)
                pygame.draw.circle(screen, (255, 255, 200), (mx, my), 3)

            # ■■ HUD panel ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
            hud_surf = pygame.Surface((W, 48), pygame.SRCALPHA)
            hud_surf.fill((0, 0, 0, 160))
            screen.blit(hud_surf, (0, 0))

            hud = font_med.render(
                f"Round {round_num}/{TOTAL_ROUNDS}     "
                f"⚽ {goals_scored}   🧤 {saves_made}", True, NEON_WHITE)
            screen.blit(hud, (W // 2 - hud.get_width() // 2, 10))

            # Controls tip
            if phase == "aim":
                tip = ("P1: Click to shoot  |  AI goalkeeper  |  ESC" if single
                       else "P1: Click to shoot  |  P2: A/D keys  |  ESC")
                tip_surf = font_small.render(tip, True, (60, 120, 60))
                screen.blit(tip_surf, (W // 2 - tip_surf.get_width() // 2, H - 24))

            pygame.display.flip()

    # ■■ Final winner ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    if goals_scored > saves_made:
        return "Player 1"
    elif saves_made > goals_scored:
        return "Computer" if single else "Player 2"
    else:
        return "Draw"