import pyray as rl

from game import SOURCES

# Layout constants
W, H = 900, 650
PANEL_X = 340
BUTTON_CX = 160
BUTTON_CY = 340
BUTTON_R = 100
ROW_H = 72


def color(rgb, a=255):
    return rl.Color(rgb[0], rgb[1], rgb[2], a)


def format_num(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 10_000:
        return f"{n/1_000:.1f}K"
    if isinstance(n, float):
        return f"{n:.1f}"
    return str(n)


def pollution_color(p):
    t = min(p / 10.0, 1.0)
    r = int(40 + 200 * t)
    g = int(200 * (1 - t) + 40)
    return rl.Color(r, g, 40, 255)


def draw_header(game):
    rl.draw_rectangle(0, 0, W, 50, rl.Color(25, 25, 40, 255))
    rl.draw_text(f"Energy: {format_num(game.energy)}", 15, 12, 24, rl.Color(0, 230, 180, 255))
    eps = game.total_eps()
    rl.draw_text(f"{format_num(eps)}/s", 280, 16, 18, rl.Color(150, 150, 180, 255))

    # Pollution meter
    poll = game.pollution()
    pc = pollution_color(poll)
    poll_label = "Clean!" if poll == 0 and eps > 0 else "Pollution"
    rl.draw_text(f"{poll_label}: {poll:.1f}", W - 220, 8, 18, pc)
    bar_x, bar_y, bar_w, bar_h = W - 220, 30, 180, 10
    rl.draw_rectangle(bar_x, bar_y, bar_w, bar_h, rl.Color(40, 40, 50, 255))
    fill = int(bar_w * min(poll / 10.0, 1.0))
    if fill > 0:
        rl.draw_rectangle(bar_x, bar_y, fill, bar_h, pc)


def draw_click_button(game, clicked):
    # flash
    if game.flash_alpha > 0:
        rl.draw_rectangle(0, 50, PANEL_X, H - 50, rl.Color(0, 230, 180, int(game.flash_alpha)))

    # button glow
    scale = 1.0 + 0.12 * game.click_anim
    r = int(BUTTON_R * scale)
    rl.draw_circle(BUTTON_CX, BUTTON_CY, r + 8, rl.Color(0, 180, 140, 40))
    rl.draw_circle(BUTTON_CX, BUTTON_CY, r + 4, rl.Color(0, 180, 140, 60))

    # button body
    btn_color = rl.Color(0, 255, 200, 255) if clicked else rl.Color(0, 200, 160, 255)
    rl.draw_circle(BUTTON_CX, BUTTON_CY, r, btn_color)
    rl.draw_circle_lines(BUTTON_CX, BUTTON_CY, r, rl.Color(255, 255, 255, 80))

    # zap icon (simple lightning bolt)
    zx, zy = BUTTON_CX, BUTTON_CY
    rl.draw_triangle(
        rl.Vector2(zx - 15, zy - 35), rl.Vector2(zx + 20, zy - 35), rl.Vector2(zx - 5, zy + 5),
        rl.Color(18, 18, 28, 220))
    rl.draw_triangle(
        rl.Vector2(zx + 15, zy + 35), rl.Vector2(zx - 20, zy + 35), rl.Vector2(zx + 5, zy - 5),
        rl.Color(18, 18, 28, 220))

    # click power text
    rl.draw_text(f"+{format_num(game.click_power)}", BUTTON_CX - 25, BUTTON_CY + BUTTON_R + 20, 20, rl.Color(0, 230, 180, 255))

    # particles
    for p in game.particles:
        alpha = int(255 * (p["life"] / 0.6))
        px = int(BUTTON_CX + p["x"])
        py = int(BUTTON_CY + p["y"])
        rl.draw_circle(px, py, 3, rl.Color(0, 255, 200, alpha))


def draw_click_upgrade(game):
    cu_cost = game.click_upgrade_cost()
    cu_y = H - 80
    cu_rect = rl.Rectangle(20, cu_y, PANEL_X - 50, 40)
    can_afford = game.energy >= cu_cost
    color = rl.Color(40, 100, 90, 255) if can_afford else rl.Color(40, 40, 50, 255)
    rl.draw_rectangle_rec(cu_rect, color)
    rl.draw_rectangle_lines_ex(cu_rect, 1, rl.Color(80, 80, 100, 255))
    rl.draw_text(f"Click Lv.{game.click_level}  ->  Lv.{game.click_level+1}", 30, cu_y + 5, 16, rl.Color(220, 220, 240, 255))
    rl.draw_text(f"Cost: {format_num(cu_cost)}", 30, cu_y + 22, 14, rl.Color(150, 150, 170, 255))
    return cu_rect


def draw_source_panel(game, visible_sources, scroll_offset):
    rl.draw_line(PANEL_X, 50, PANEL_X, H, rl.Color(50, 50, 70, 255))

    panel_top = 55
    panel_h = H - panel_top - 5
    rl.begin_scissor_mode(PANEL_X + 1, panel_top, W - PANEL_X - 1, panel_h)

    buy_rects = {}

    for vi, idx in enumerate(visible_sources):
        src = SOURCES[idx]
        y = panel_top + vi * ROW_H - int(scroll_offset)
        if y + ROW_H < panel_top or y > H:
            continue

        unlocked = game.total_energy >= src["unlock"] or game.levels[idx] > 0
        row_rect = rl.Rectangle(PANEL_X + 5, y + 2, W - PANEL_X - 12, ROW_H - 4)

        # row bg
        bg = rl.Color(30, 30, 45, 255) if unlocked else rl.Color(25, 25, 35, 180)
        rl.draw_rectangle_rec(row_rect, bg)

        # color accent bar
        accent = color(src["color"]) if unlocked else rl.Color(60, 60, 60, 255)
        rl.draw_rectangle(PANEL_X + 5, y + 2, 4, ROW_H - 4, accent)

        tx = PANEL_X + 16

        if not unlocked:
            rl.draw_text(f"??? (need {format_num(src['unlock'])} total energy)", tx, y + 18, 16, rl.Color(100, 100, 120, 255))
            p = src["pollution"]
            hint = "Very Dirty" if p >= 8 else "Dirty" if p >= 5 else "Moderate" if p >= 3 else "Clean" if p >= 1 else "Zero Emission"
            rl.draw_text(hint, tx, y + 40, 12, rl.Color(80, 80, 100, 255))
        else:
            rl.draw_text(f"{src['name']}  Lv.{game.levels[idx]}", tx, y + 6, 16, rl.Color(220, 220, 240, 255))

            e = game.eps(idx)
            rl.draw_text(f"{format_num(e)}/s", tx, y + 26, 14, rl.Color(0, 200, 160, 255))

            p = src["pollution"]
            plabel = f"Pollution: {p}" if p > 0 else "Zero Emission!"
            rl.draw_text(plabel, tx + 100, y + 26, 12, pollution_color(p))

            # buy button
            cost = game.cost(idx)
            can_afford = game.energy >= cost
            bw, bh = 100, 28
            bx = W - bw - 18
            by = y + (ROW_H - bh) // 2
            btn_rect = rl.Rectangle(bx, by, bw, bh)
            btn_col = rl.Color(40, 100, 90, 255) if can_afford else rl.Color(40, 40, 50, 255)
            rl.draw_rectangle_rec(btn_rect, btn_col)
            rl.draw_rectangle_lines_ex(btn_rect, 1, rl.Color(80, 80, 100, 255))

            label = f"Buy {format_num(cost)}"
            rl.draw_text(label, bx + 6, by + 7, 14, rl.Color(200, 200, 220, 255))

            buy_rects[idx] = btn_rect

    rl.end_scissor_mode()
    return buy_rects
