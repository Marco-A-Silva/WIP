import time, pygame

notifications = []

def addNotification(text, duration=1):
    notifications.append({
        "text": text,
        "expires": time.time() + duration
    })

def drawNotifications(display):
    now = time.time()
    y_offset = 20

    for n in notifications[:]:
        if now > n["expires"]:
            notifications.remove(n)
            continue

        _drawSingle(display, n, y_offset)
        y_offset += 50


def _drawSingle(display, notification, y_offset):
    screen, fonts, _ = display
    font = fonts[1]

    max_width = screen.get_width() - 100
    lines = wrap_text(notification["text"], font, max_width)

    rendered_lines = [font.render(line, True, (255, 255, 255)) for line in lines]

    line_height = font.get_height()
    text_height = line_height * len(rendered_lines)
    text_width = max(r.get_width() for r in rendered_lines)

    padding_x, padding_y = 15, 10

    box_rect = pygame.Rect(
        (screen.get_width() - text_width) // 2 - padding_x,
        50 + y_offset - padding_y,
        text_width + padding_x * 2,
        text_height + padding_y * 2
    )

    pygame.draw.rect(screen, (50, 50, 50), box_rect, border_radius=10)
    pygame.draw.rect(screen, (200, 200, 255), box_rect, 2, border_radius=10)

    y = box_rect.y + padding_y
    for rendered in rendered_lines:
        rect = rendered.get_rect(centerx=screen.get_width() // 2, y=y)
        screen.blit(rendered, rect)
        y += line_height


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def addHover(display, objRect, orientation, *args):
    screen, font, color = display
    mouse_pos = pygame.mouse.get_pos()

    if not objRect.collidepoint(mouse_pos):
        return

    text = " ".join(str(arg) for arg in args)
    maxWidth = 200
    lines = wrap_text(text, font[2], maxWidth)

    line_height = font[2].get_height()
    padding = 6

    # calcular tamaño total del hover
    hover_w = max(font[2].size(line)[0] for line in lines) + padding * 2
    hover_h = len(lines) * line_height + padding * 2

    gap = 6

    match orientation:
        case "top":
            hover_x = objRect.centerx - hover_w // 2
            hover_y = objRect.top - hover_h - gap

        case "bot":
            hover_x = objRect.centerx - hover_w // 2
            hover_y = objRect.bottom + gap

        case "left":
            hover_x = objRect.left - hover_w - gap
            hover_y = objRect.centery - hover_h // 2

        case "right":
            hover_x = objRect.right + gap
            hover_y = objRect.centery - hover_h // 2


    # clamp horizontal
    hover_x = max(4, min(hover_x, screen.get_width() - hover_w - 4))

    # si no entra arriba, va abajo
    if hover_y < 0:
        hover_y = objRect.bottom + 6

    hover_rect = pygame.Rect(hover_x, hover_y, hover_w, hover_h)

    # fondo
    pygame.draw.rect(screen, (20, 20, 25), hover_rect, border_radius=6)
    pygame.draw.rect(screen, (90, 90, 100), hover_rect, 1, border_radius=6)

    # texto
    y = hover_y + padding
    for line in lines:
        surf = font[2].render(line, True, (230, 230, 240))
        screen.blit(surf, (hover_x + padding, y))
        y += line_height
