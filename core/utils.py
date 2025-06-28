import pygame

def point_in_polygon(point, polygon):
    """
    Determine if a point is inside a polygon using the ray casting algorithm.

    Args:
        point (tuple): Coordinates as (x, y).
        polygon (list[tuple]): List of (x, y) vertices defining the polygon.

    Returns:
        bool: True if the point is inside the polygon, False otherwise.
    """
    n = len(polygon)
    inside = False

    px, py = point
    for i in range(n):
        j = (i - 1) % n
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and \
                (px < (xj - xi) * (py - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
    return inside


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    """
    Split text into lines so that each line fits within a given width.

    Args:
        text (str): Text to wrap.
        font (pygame.font.Font): Font used to measure text.
        max_width (int): Maximum allowed width in pixels.

    Returns:
        list[str]: Wrapped lines of text.
    """
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue

        words = paragraph.split(" ")
        line = words[0]

        for word in words[1:]:
            test_line = f"{line} {word}"
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)

    return lines


def draw_wrapped_text_centered(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    rect: pygame.Rect,
    scroll: int,
    color: tuple[int, int, int]
) -> None:
    """
    Draw wrapped text centered within a rectangle and apply vertical scrolling.

    Args:
        surface (pygame.Surface): Target surface to draw on.
        text (str): Text content to render.
        font (pygame.font.Font): Font used to render the text.
        rect (pygame.Rect): Area within which to draw the text.
        scroll (int): Vertical scroll offset in pixels.
        color (tuple[int, int, int]): Text color as an RGB tuple.

    Returns:
        None
    """
    prev_clip = surface.get_clip()
    surface.set_clip(rect)

    lines = wrap_text(text, font, rect.width)
    line_height = font.get_height()
    total_height = line_height * len(lines)

    y_start = rect.y + max((rect.height - total_height) // 2, 0) - scroll
    y = y_start

    for line in lines:
        if y + line_height < rect.y:
            y += line_height
            continue
        if y > rect.y + rect.height:
            break

        rendered = font.render(line, True, color)
        x = rect.x + (rect.width - rendered.get_width()) // 2
        surface.blit(rendered, (x, y))
        y += line_height

    surface.set_clip(prev_clip)
