# =============================================================
# menu.py - Student 2
# UPGRADED Main menu screen - Arcade Style Dashboard
# =============================================================
import pygame
import math
import random

# ■■ Color constants ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
BG_DARK      = (8, 8, 20)
NEON_BLUE    = (0, 200, 255)
NEON_PINK    = (255, 0, 120)
NEON_PURPLE  = (160, 0, 255)
NEON_ORANGE  = (255, 140, 0)
NEON_GREEN   = (0, 255, 140)
WHITE        = (255, 255, 255)
GRAY         = (120, 120, 140)
DARK_PANEL   = (15, 15, 35)
GOLD         = (255, 215, 0)

# ■■ Game button data: (label, emoji, return_value, neon_color) ■■
GAME_BUTTONS = [
    ("Table Tennis",   "🏓", "table_tennis",   (76,  201, 240)),
    ("Penalty Kicks",  "⚽", "penalty_kicks",  (255,  40, 133)),
    ("Pool Billiards", "🎱", "pool",           (140,  20, 255)),
    ("Red Hands",      "✋", "red_hands",      (255, 140,   0)),
]

# ■■ Particle class for animated background ■■■■■■■■■■■■■■■■■■■
class Particle:
    def __init__(self, W, H):
        self.W = W
        self.H = H
        self.reset()

    def reset(self):
        self.x  = random.randint(0, self.W)
        self.y  = random.randint(0, self.H)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-0.6, -0.15)
        self.size   = random.randint(1, 3)
        self.alpha  = random.randint(60, 200)
        self.color  = random.choice([NEON_BLUE, NEON_PINK, NEON_PURPLE, NEON_GREEN])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 0.4
        if self.alpha < 0 or self.y < -10:
            self.reset()
            self.y = self.H + 5

    def draw(self, screen):
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        col = (*self.color, max(0, int(self.alpha)))
        pygame.draw.circle(s, col, (self.size, self.size), self.size)
        screen.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


# ■■ Draw a glowing neon rectangle ■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def draw_glow_rect(screen, rect, color, glow_size=8, alpha=60):
    """Draw a soft glow behind a rectangle."""
    for i in range(glow_size, 0, -2):
        glow_surf = pygame.Surface(
            (rect.width + i * 2, rect.height + i * 2), pygame.SRCALPHA
        )
        a = int(alpha * (i / glow_size) * 0.5)
        pygame.draw.rect(
            glow_surf,
            (*color, a),
            (0, 0, rect.width + i * 2, rect.height + i * 2),
            border_radius=14
        )
        screen.blit(glow_surf, (rect.x - i, rect.y - i))


# ■■ Draw a single game button ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def draw_game_button(screen, label, emoji, rect, color, is_hovered, font_main, font_small, tick):
    r = pygame.Rect(rect)

    if is_hovered:
        # Draw outer glow
        draw_glow_rect(screen, r, color, glow_size=14, alpha=90)
        # Slightly lighter fill
        fill_color = tuple(min(c + 30, 255) for c in color)
        border_color = WHITE
        text_color = WHITE
    else:
        fill_color = tuple(c // 3 for c in color)  # Dark tinted fill
        border_color = tuple(c // 2 for c in color)
        text_color = tuple(180 + c // 6 for c in color)

    # Draw filled rounded rect
    pygame.draw.rect(screen, fill_color, r, border_radius=12)

    # Animated border when hovered (brightness pulse)
    if is_hovered:
        pulse = 0.6 + 0.4 * abs(math.sin(tick * 0.05))
        bc = tuple(int(c * pulse) for c in color)
        pygame.draw.rect(screen, bc, r, 3, border_radius=12)
    else:
        pygame.draw.rect(screen, border_color, r, 2, border_radius=12)

    # Emoji on left side
    emoji_surf = font_small.render(emoji, True, WHITE)
    screen.blit(emoji_surf, (r.x + 18, r.y + (r.height - emoji_surf.get_height()) // 2))

    # Label text centered
    label_surf = font_main.render(label, True, text_color)
    screen.blit(label_surf, (
        r.x + (r.width - label_surf.get_width()) // 2,
        r.y + (r.height - label_surf.get_height()) // 2
    ))

    # Arrow on right side when hovered
    if is_hovered:
        arrow = font_small.render("▶", True, WHITE)
        screen.blit(arrow, (r.right - 36, r.y + (r.height - arrow.get_height()) // 2))


# ■■ Draw animated scanline overlay ■■■■■■■■■■■■■■■■■■■■■■■■■■■
def draw_scanlines(screen, W, H):
    scan_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 4):
        pygame.draw.line(scan_surf, (0, 0, 0, 18), (0, y), (W, y))
    screen.blit(scan_surf, (0, 0))


# ■■ Draw grid background ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def draw_grid(screen, W, H, tick):
    """Animated perspective grid (arcade floor effect)."""
    grid_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    grid_color = (0, 80, 140, 35)

    # Horizontal lines
    for y in range(0, H, 40):
        pygame.draw.line(grid_surf, grid_color, (0, y), (W, y), 1)

    # Vertical lines
    for x in range(0, W, 60):
        pygame.draw.line(grid_surf, grid_color, (x, 0), (x, H), 1)

    screen.blit(grid_surf, (0, 0))


# ■■ Main show_menu function ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
def show_menu(screen, clock):
    """
    Display the upgraded arcade-style main menu.
    Returns: 'table_tennis', 'penalty_kicks', 'pool', 'red_hands', or 'quit'
    """
    W, H = screen.get_size()

    # ■■ Fonts ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    font_title  = pygame.font.SysFont("Consolas", 52, bold=True)
    font_sub    = pygame.font.SysFont("Consolas", 15)
    font_btn    = pygame.font.SysFont("Consolas", 21, bold=True)
    font_emoji  = pygame.font.SysFont("Segoe UI Emoji", 22)
    font_hint   = pygame.font.SysFont("Consolas", 14)

    # ■■ Particles ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    particles = [Particle(W, H) for _ in range(80)]

    # ■■ Button layout ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    btn_w = 500
    btn_h = 56
    btn_x = (W - btn_w) // 2
    btn_start_y = 190
    btn_gap = 68

    buttons = []
    for i, (label, emoji, key, color) in enumerate(GAME_BUTTONS):
        rect = (btn_x, btn_start_y + i * btn_gap, btn_w, btn_h)
        buttons.append((label, emoji, key, rect, color))

    # Quit button
    quit_rect = (W // 2 - 140, btn_start_y + 4 * btn_gap + 10, 280, 42)

    tick = 0

    while True:
        tick += 1
        mx, my = pygame.mouse.get_pos()

        # ■■ Event handling ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check game buttons
                for label, emoji, key, rect, color in buttons:
                    if pygame.Rect(rect).collidepoint(mx, my):
                        return key
                # Check quit button
                if pygame.Rect(quit_rect).collidepoint(mx, my):
                    return "quit"

        # ■■ Draw background ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        screen.fill(BG_DARK)
        draw_grid(screen, W, H, tick)

        # ■■ Draw particles ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        for p in particles:
            p.update()
            p.draw(screen)

        # ■■ Title glow ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        # Shadow layer
        title_shadow = font_title.render("2 PLAYER GAMES", True, NEON_PURPLE)
        screen.blit(title_shadow, (W // 2 - title_shadow.get_width() // 2 + 3, 45 + 3))

        # Pulsing main title color
        pulse = 0.7 + 0.3 * abs(math.sin(tick * 0.03))
        title_r = int(255 * pulse)
        title_g = int(60 + 40 * pulse)
        title_color = (title_r, title_g, 120)
        title_surf = font_title.render("2 PLAYER GAMES", True, title_color)
        screen.blit(title_surf, (W // 2 - title_surf.get_width() // 2, 45))

        # Subtitle
        sub = font_sub.render("— SELECT YOUR GAME —", True, GRAY)
        screen.blit(sub, (W // 2 - sub.get_width() // 2, 108))

        # Decorative line under title
        line_y = 130
        line_w = 360
        line_x = W // 2 - line_w // 2
        pulse2 = 0.5 + 0.5 * abs(math.sin(tick * 0.04))
        line_col = (int(0 + 100 * pulse2), int(150 + 105 * pulse2), 255)
        pygame.draw.line(screen, line_col, (line_x, line_y), (line_x + line_w, line_y), 2)
        # Small diamonds on ends
        pygame.draw.polygon(screen, line_col, [
            (line_x - 6, line_y),
            (line_x, line_y - 5),
            (line_x + 6, line_y),
            (line_x, line_y + 5),
        ])
        pygame.draw.polygon(screen, line_col, [
            (line_x + line_w - 6, line_y),
            (line_x + line_w, line_y - 5),
            (line_x + line_w + 6, line_y),
            (line_x + line_w, line_y + 5),
        ])

        # ■■ Draw game buttons ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        for label, emoji, key, rect, color in buttons:
            hovered = pygame.Rect(rect).collidepoint(mx, my)
            draw_game_button(
                screen, label, emoji, rect, color,
                hovered, font_btn, font_emoji, tick
            )

        # ■■ Quit button ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        quit_hovered = pygame.Rect(quit_rect).collidepoint(mx, my)
        qr = pygame.Rect(quit_rect)
        q_fill  = (60, 20, 20) if quit_hovered else (25, 10, 10)
        q_border = (200, 60, 60) if quit_hovered else (100, 40, 40)
        pygame.draw.rect(screen, q_fill, qr, border_radius=10)
        pygame.draw.rect(screen, q_border, qr, 2, border_radius=10)
        quit_text = font_hint.render("✕  QUIT", True, (220, 80, 80) if quit_hovered else (140, 60, 60))
        screen.blit(quit_text, (
            qr.x + (qr.width - quit_text.get_width()) // 2,
            qr.y + (qr.height - quit_text.get_height()) // 2
        ))

        # ■■ Scanline overlay ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        draw_scanlines(screen, W, H)

        # ■■ Bottom hint ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
        hint = font_hint.render("CLICK A GAME TO START  |  ESC TO QUIT", True, (60, 60, 90))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 28))

        pygame.display.flip()
        clock.tick(60)