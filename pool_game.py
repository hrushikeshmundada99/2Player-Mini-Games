# =============================================================
# pool_game.py - Student 3 - DIFFICULTY: HARD (5/5)
# ARCADE EDITION - Neon Pool Billiards
# =============================================================
import pygame
import math
import random

def draw_glow_circle(screen, color, pos, radius, glow=10, alpha=80):
    for i in range(glow, 0, -2):
        s = pygame.Surface((radius * 2 + i * 2, radius * 2 + i * 2), pygame.SRCALPHA)
        a = int(alpha * (i / glow) * 0.5)
        pygame.draw.circle(s, (*color, a), (radius + i, radius + i), radius + i)
        screen.blit(s, (pos[0] - radius - i, pos[1] - radius - i))
    pygame.draw.circle(screen, color, pos, radius)

def run_pool(screen, clock, single=False):
    """
    Arcade Neon Pool Billiards.
    single=True  -> Player 1 vs AI
    single=False -> Player 1 vs Player 2
    Returns: 'Player 1', 'Player 2', 'Computer', or 'Draw'
    """
    W, H = screen.get_size()

    # ■■ Colors ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    FELT_GREEN  = (0, 55, 30)
    FELT_LIGHT  = (0, 70, 38)
    WOOD        = (60, 30, 10)
    WOOD_LIGHT  = (90, 50, 20)
    WHITE       = (255, 255, 255)
    BLACK       = (5, 5, 5)
    POCKET_C    = (5, 5, 5)
    POCKET_GLOW = (0, 180, 100)
    P1_COLOR    = (255, 60, 120)
    P2_COLOR    = (0, 200, 255)
    NEON_WHITE  = (220, 255, 220)
    GOLD        = (255, 215, 0)
    CUE_COLOR   = (220, 170, 80)

    # ■■ Physics ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    BALL_RADIUS = 13
    FRICTION    = 0.985
    MAX_POWER   = 18
    TABLE_PAD   = 50

    # ■■ Pocket positions ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    p = TABLE_PAD
    pockets = [
        (p, p), (W // 2, p), (W - p, p),
        (p, H - p), (W // 2, H - p), (W - p, H - p),
    ]

    # ■■ Create balls ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    balls = []
    balls.append({
        "x": 200.0, "y": float(H // 2),
        "vx": 0.0,  "vy": 0.0,
        "color": WHITE, "pocketed": False, "owner": "cue"
    })

    rack_center_x = int(W * 2 / 3)
    rack_center_y = H // 2
    rack_colors = [
        P1_COLOR, P2_COLOR, P1_COLOR, P2_COLOR, (80, 80, 80),
        P2_COLOR, P1_COLOR, P1_COLOR, P2_COLOR, P1_COLOR, P2_COLOR, P1_COLOR,
    ]
    idx = 0
    for row in range(4):
        for col in range(row + 1):
            if idx >= len(rack_colors):
                break
            c   = rack_colors[idx]; idx += 1
            bx  = rack_center_x + row * (BALL_RADIUS * 2 + 2)
            by  = rack_center_y + col * (BALL_RADIUS * 2 + 2) - row * (BALL_RADIUS + 1)
            own = "p1" if c == P1_COLOR else "p2" if c == P2_COLOR else "8"
            balls.append({
                "x": float(bx), "y": float(by),
                "vx": 0.0, "vy": 0.0,
                "color": c, "pocketed": False, "owner": own
            })

    # ■■ Game state ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    score        = {"p1": 0, "p2": 0}
    turn         = "p1"
    aiming       = False
    aim_start    = None
    ai_thinking  = False
    ai_think_until = 0
    cue_ball     = balls[0]

    # ■■ Pocket flash effects ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    pocket_flashes = {}   # pocket_index -> frames_remaining

    # ■■ Fonts ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    font_hud   = pygame.font.SysFont("Consolas", 20, bold=True)
    font_small = pygame.font.SysFont("Consolas", 14)

    tick = 0

    def all_balls_stopped():
        return all(abs(b["vx"]) < 0.08 and abs(b["vy"]) < 0.08
                   for b in balls if not b["pocketed"])

    def check_pockets():
        for bi, b in enumerate(balls):
            if b["pocketed"]:
                continue
            for pi, (px, py) in enumerate(pockets):
                dist = math.hypot(b["x"] - px, b["y"] - py)
                if dist < BALL_RADIUS + 10:
                    b["pocketed"] = True
                    if b["owner"] == "p1": score["p1"] += 1
                    elif b["owner"] == "p2": score["p2"] += 1
                    # Trigger flash on this pocket
                    owner_col = b["color"]
                    pocket_flashes[pi] = (20, owner_col)

    def ai_take_shot():
        if cue_ball["pocketed"]: return
        my_balls = [b for b in balls if not b["pocketed"] and b["owner"] == "p2"]
        if not my_balls: return
        target = min(my_balls, key=lambda b: math.hypot(
            b["x"] - cue_ball["x"], b["y"] - cue_ball["y"]))
        dx   = target["x"] - cue_ball["x"]
        dy   = target["y"] - cue_ball["y"]
        dist = math.hypot(dx, dy) or 1
        pwr  = random.uniform(8, 13)
        cue_ball["vx"] = (dx / dist) * pwr
        cue_ball["vy"] = (dy / dist) * pwr

    # ■■ Main loop ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    while True:
        clock.tick(60)
        tick += 1
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:   return "Draw"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "Draw"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if turn == "p1" and not cue_ball["pocketed"] and all_balls_stopped():
                    aiming    = True
                    aim_start = (mx, my)
            if event.type == pygame.MOUSEBUTTONUP and aiming:
                aiming = False
                dx     = aim_start[0] - mx
                dy     = aim_start[1] - my
                power  = min(math.hypot(dx, dy) / 10, MAX_POWER)
                dist   = math.hypot(dx, dy) or 1
                cue_ball["vx"] = (dx / dist) * power
                cue_ball["vy"] = (dy / dist) * power
                turn = "p2"

        # ■■ AI turn ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        if single and turn == "p2" and all_balls_stopped():
            if not ai_thinking:
                ai_thinking    = True
                ai_think_until = pygame.time.get_ticks() + 1500
            if pygame.time.get_ticks() >= ai_think_until:
                ai_thinking = False
                ai_take_shot()
                turn = "p1"

        # ■■ Physics ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        for b in balls:
            if b["pocketed"]: continue
            b["x"] += b["vx"];  b["y"] += b["vy"]
            b["vx"] *= FRICTION; b["vy"] *= FRICTION
            if abs(b["vx"]) < 0.05: b["vx"] = 0
            if abs(b["vy"]) < 0.05: b["vy"] = 0
            if b["x"] - BALL_RADIUS < TABLE_PAD:
                b["x"] = TABLE_PAD + BALL_RADIUS; b["vx"] *= -0.8
            if b["x"] + BALL_RADIUS > W - TABLE_PAD:
                b["x"] = W - TABLE_PAD - BALL_RADIUS; b["vx"] *= -0.8
            if b["y"] - BALL_RADIUS < TABLE_PAD:
                b["y"] = TABLE_PAD + BALL_RADIUS; b["vy"] *= -0.8
            if b["y"] + BALL_RADIUS > H - TABLE_PAD:
                b["y"] = H - TABLE_PAD - BALL_RADIUS; b["vy"] *= -0.8

        # ■■ Ball collisions ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        active = [b for b in balls if not b["pocketed"]]
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a = active[i]; b = active[j]
                dx   = b["x"] - a["x"]; dy = b["y"] - a["y"]
                dist = math.hypot(dx, dy)
                if 0 < dist < BALL_RADIUS * 2:
                    nx = dx / dist; ny = dy / dist
                    overlap = BALL_RADIUS * 2 - dist
                    a["x"] -= nx * overlap / 2; a["y"] -= ny * overlap / 2
                    b["x"] += nx * overlap / 2; b["y"] += ny * overlap / 2
                    rel = ((a["vx"] - b["vx"]) * nx + (a["vy"] - b["vy"]) * ny)
                    a["vx"] -= rel * nx * 0.9; a["vy"] -= rel * ny * 0.9
                    b["vx"] += rel * nx * 0.9; b["vy"] += rel * ny * 0.9

        check_pockets()

        # ■■ Win condition ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        remaining = [b for b in balls
                     if not b["pocketed"] and b["owner"] not in ("cue", "8")]
        if not remaining:
            if score["p1"] > score["p2"]:   return "Player 1"
            elif score["p2"] > score["p1"]: return "Computer" if single else "Player 2"
            else:                            return "Draw"

        # ■■■■■■■■■■■■■■■■ DRAWING ■■■■■■■■■■■■■■■■■■■■■■■■■■
        screen.fill(WOOD)

        # Wood border detail
        pygame.draw.rect(screen, WOOD_LIGHT,
                         (TABLE_PAD - 18, TABLE_PAD - 18,
                          W - 2 * (TABLE_PAD - 18), H - 2 * (TABLE_PAD - 18)),
                         border_radius=10)

        # Felt surface
        pygame.draw.rect(screen, FELT_GREEN,
                         (TABLE_PAD, TABLE_PAD,
                          W - 2 * TABLE_PAD, H - 2 * TABLE_PAD))

        # Felt diamond pattern (subtle)
        for gy in range(TABLE_PAD, H - TABLE_PAD, 40):
            for gx in range(TABLE_PAD, W - TABLE_PAD, 40):
                pygame.draw.rect(screen, FELT_LIGHT, (gx, gy, 20, 20))

        # Table border line
        pygame.draw.rect(screen, (80, 50, 20),
                         (TABLE_PAD, TABLE_PAD,
                          W - 2 * TABLE_PAD, H - 2 * TABLE_PAD), 3)

        # Pockets with glow
        for pi, (px, py) in enumerate(pockets):
            # Pocket flash
            if pi in pocket_flashes:
                frames, pcol = pocket_flashes[pi]
                if frames > 0:
                    draw_glow_circle(screen, pcol, (px, py),
                                     20, glow=14, alpha=int(80 * frames / 20))
                    pocket_flashes[pi] = (frames - 1, pcol)
                else:
                    del pocket_flashes[pi]
            pygame.draw.circle(screen, POCKET_C, (px, py), 18)
            # Subtle green rim
            pygame.draw.circle(screen, (0, 100, 40), (px, py), 18, 2)

        # Balls
        for b in balls:
            if b["pocketed"]: continue
            pos = (int(b["x"]), int(b["y"]))
            # Glow for colored balls
            if b["owner"] != "cue":
                draw_glow_circle(screen, b["color"], pos,
                                 BALL_RADIUS, glow=8, alpha=60)
            else:
                # White cue ball - subtle glow
                draw_glow_circle(screen, (200, 200, 255), pos,
                                 BALL_RADIUS, glow=10, alpha=50)
            pygame.draw.circle(screen, b["color"], pos, BALL_RADIUS)
            # Shine dot
            shine_x = pos[0] - BALL_RADIUS // 3
            shine_y = pos[1] - BALL_RADIUS // 3
            pygame.draw.circle(screen, (255, 255, 255, 120),
                               (shine_x, shine_y), 3)
            pygame.draw.circle(screen, BLACK, pos, BALL_RADIUS, 1)

        # Cue stick while aiming
        if aiming and not cue_ball["pocketed"]:
            dx = cue_ball["x"] - mx; dy = cue_ball["y"] - my
            end_x = int(cue_ball["x"] + dx * 0.4)
            end_y = int(cue_ball["y"] + dy * 0.4)
            # Cue stick shadow
            pygame.draw.line(screen, (30, 20, 5), (mx + 2, my + 2), (end_x + 2, end_y + 2), 7)
            # Cue stick body
            pygame.draw.line(screen, CUE_COLOR, (mx, my), (end_x, end_y), 6)
            # Cue tip highlight
            pygame.draw.line(screen, WHITE, (mx, my),
                             (mx + int(dx / (math.hypot(dx, dy) or 1) * 5),
                              my + int(dy / (math.hypot(dx, dy) or 1) * 5)), 2)
            # Aim dotted line
            norm = math.hypot(dx, dy) or 1
            aim_end_x = int(cue_ball["x"] + (dx / norm) * -200)
            aim_end_y = int(cue_ball["y"] + (dy / norm) * -200)
            for t in range(0, 200, 12):
                dot_x = int(cue_ball["x"] + (dx / norm) * -t)
                dot_y = int(cue_ball["y"] + (dy / norm) * -t)
                pygame.draw.circle(screen, (255, 255, 100, 120), (dot_x, dot_y), 2)

            # Power bar
            power = min(math.hypot(dx, dy) / 10, MAX_POWER)
            bar_w = int((power / MAX_POWER) * 160)
            pygame.draw.rect(screen, (30, 30, 30), (18, H - 44, 160, 16),
                             border_radius=8)
            bar_color = (
                int(80 + 175 * (power / MAX_POWER)),
                int(200 - 160 * (power / MAX_POWER)),
                60
            )
            if bar_w > 0:
                pygame.draw.rect(screen, bar_color, (18, H - 44, bar_w, 16),
                                 border_radius=8)
            pygame.draw.rect(screen, WHITE, (18, H - 44, 160, 16), 1,
                             border_radius=8)
            pct = font_small.render(
                f"Power: {int(power * 100 / MAX_POWER)}%", True, WHITE)
            screen.blit(pct, (185, H - 46))

        # AI thinking
        if ai_thinking:
            pulse = 0.5 + 0.5 * math.sin(tick * 0.1)
            think_col = (int(200 * pulse), int(215 * pulse), 0)
            think = font_hud.render("AI thinking...", True, think_col)
            screen.blit(think, (W // 2 - think.get_width() // 2, H // 2 - 12))

        # ■■ HUD ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        hud_s = pygame.Surface((W, 36), pygame.SRCALPHA)
        hud_s.fill((0, 0, 0, 160))
        screen.blit(hud_s, (0, 0))

        p2_lbl  = "AI" if single else "P2"
        turn_col = P1_COLOR if turn == "p1" else P2_COLOR
        hud_txt  = (f"P1 ● {score['p1']}    {p2_lbl} ● {score['p2']}"
                    f"     TURN: {turn.upper()}")
        hud_surf = font_hud.render(hud_txt, True, turn_col)
        screen.blit(hud_surf, (W // 2 - hud_surf.get_width() // 2, 8))

        # P1 / P2 score dots
        for i in range(6):
            filled = i < score["p1"]
            c = P1_COLOR if filled else (40, 20, 30)
            pygame.draw.circle(screen, c, (30 + i * 14, H - 20), 5)
        for i in range(6):
            filled = i < score["p2"]
            c = P2_COLOR if filled else (10, 30, 40)
            pygame.draw.circle(screen, c, (W - 30 - i * 14, H - 20), 5)

        # Bottom tip
        if turn == "p1":
            tip = "Click & drag AWAY from cue ball, release to shoot  |  ESC: Exit"
        else:
            tip = ("AI's turn – watch!" if single
                   else "P2: Click & drag to shoot  |  ESC: Exit")
        tip_s = font_small.render(tip, True, (80, 120, 80))
        screen.blit(tip_s, (W // 2 - tip_s.get_width() // 2, H - 20))

        pygame.display.flip()