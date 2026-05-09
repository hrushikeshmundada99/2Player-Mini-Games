# =============================================================
# mode_select.py - Student 3
# Mode selection: 1 Player vs AI OR 2 Players
# =============================================================

import pygame

def show_mode_select(screen, clock):
    """
    Let players choose game mode.
    Returns: 'single' | 'two' | 'back'
    """
    W, H = screen.get_size()

    # Colors
    DARK  = (26, 26, 46)
    WHITE = (255, 255, 255)
    GREEN = (39, 174, 96)
    CYAN  = (76, 201, 240)
    GRAY  = (100, 100, 100)
    GOLD  = (255, 215, 0)
    LIGHT = (180, 180, 180)

    # Buttons: (label, return_value, rect_coords, color)
    # rect_coords: (x, y, width, height)
    buttons = [
        ("1 Player (vs Computer AI)", "single", (220, 200, 460, 65), GREEN),
        ("2 Players (vs Friend)",      "two",    (220, 290, 460, 65), CYAN),
        ("Back to Menu",               "back",   (300, 390, 300, 45), GRAY),
    ]

    # Fonts
    font_title = pygame.font.SysFont("Arial", 34, bold=True)
    font_desc  = pygame.font.SysFont("Arial", 14)
    font_btn   = pygame.font.SysFont("Arial", 21, bold=True)

    descriptions = {
        "single": "You play against the Computer",
        "two":    "Two players on one device",
        "back":   "",
    }

    while True:
        mx, my = pygame.mouse.get_pos()

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "back"
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"

            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, key, rect, base_color in buttons:
                    if pygame.Rect(rect).collidepoint(mx, my):
                        return key

        # 2. Drawing Logic
        screen.fill(DARK)

        # Title
        title = font_title.render("Select Game Mode", True, WHITE)
        screen.blit(title, (W // 2 - title.get_width() // 2, 110))

        # Draw buttons
        for label, key, rect, base_color in buttons:
            r = pygame.Rect(rect)
            hovered = r.collidepoint(mx, my)

            # Highlight color if hovered
            color = tuple(min(c + 30, 255) for c in base_color) if hovered else base_color
            
            # Draw button body and border
            pygame.draw.rect(screen, color, r, border_radius=12)
            pygame.draw.rect(screen, WHITE, r, 2, border_radius=12)

            # Draw button text
            lbl = font_btn.render(label, True, WHITE)
            screen.blit(lbl, (
                r.x + (r.width - lbl.get_width()) // 2, 
                r.y + (r.height - lbl.get_height()) // 2
            ))

            # Show description text below hovered button
            if hovered and descriptions[key]:
                d = font_desc.render(descriptions[key], True, GOLD)
                screen.blit(d, (W // 2 - d.get_width() // 2, r.bottom + 6))

        # Footer hint
        hint = font_desc.render("Press ESC to go back", True, LIGHT)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 35))

        # 3. Update Display
        pygame.display.flip()
        clock.tick(60)

   