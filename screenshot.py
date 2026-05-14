"""Take screenshots of the game at different states for the README."""
import pyray as rl
import math
from main import Game, SOURCES, format_num, pollution_color

W, H = 900, 650

def draw_game(game):
    PANEL_X = 340
    BUTTON_CX = 160
    BUTTON_CY = 340
    BUTTON_R = 100
    row_h = 72

    rl.clear_background(rl.Color(18, 18, 28, 255))

    # Header bar
    rl.draw_rectangle(0, 0, W, 50, rl.Color(25, 25, 40, 255))
    rl.draw_text(f"Energy: {format_num(game.energy)}", 15, 12, 24, rl.Color(0, 230, 180, 255))
    eps = game.total_eps()
    rl.draw_text(f"{format_num(eps)}/s", 280, 16, 18, rl.Color(150, 150, 180, 255))

    poll = game.pollution()
    pc = pollution_color(poll)
    poll_label = "Pollution" if not (poll == 0 and eps > 0) else "Clean!"
    rl.draw_text(f"{poll_label}: {poll:.1f}", W - 220, 8, 18, pc)
    bar_x, bar_y, bar_w, bar_h = W - 220, 30, 180, 10
    rl.draw_rectangle(bar_x, bar_y, bar_w, bar_h, rl.Color(40, 40, 50, 255))
    fill = int(bar_w * min(poll / 10.0, 1.0))
    if fill > 0:
        rl.draw_rectangle(bar_x, bar_y, fill, bar_h, pc)

    # Button
    r = BUTTON_R
    rl.draw_circle(BUTTON_CX, BUTTON_CY, r + 8, rl.Color(0, 180, 140, 40))
    rl.draw_circle(BUTTON_CX, BUTTON_CY, r + 4, rl.Color(0, 180, 140, 60))
    rl.draw_circle(BUTTON_CX, BUTTON_CY, r, rl.Color(0, 200, 160, 255))
    rl.draw_circle_lines(BUTTON_CX, BUTTON_CY, r, rl.Color(255, 255, 255, 80))
    zx, zy = BUTTON_CX, BUTTON_CY
    rl.draw_triangle(
        rl.Vector2(zx - 15, zy - 35), rl.Vector2(zx + 20, zy - 35), rl.Vector2(zx - 5, zy + 5),
        rl.Color(18, 18, 28, 220))
    rl.draw_triangle(
        rl.Vector2(zx + 15, zy + 35), rl.Vector2(zx - 20, zy + 35), rl.Vector2(zx + 5, zy - 5),
        rl.Color(18, 18, 28, 220))
    rl.draw_text(f"+{format_num(game.click_power)}", BUTTON_CX - 25, BUTTON_CY + BUTTON_R + 20, 20, rl.Color(0, 230, 180, 255))

    # Click upgrade
    cu_cost = game.click_upgrade_cost()
    cu_y = H - 80
    cu_rect = rl.Rectangle(20, cu_y, PANEL_X - 50, 40)
    can_afford_cu = game.energy >= cu_cost
    cu_color = rl.Color(40, 100, 90, 255) if can_afford_cu else rl.Color(40, 40, 50, 255)
    rl.draw_rectangle_rec(cu_rect, cu_color)
    rl.draw_rectangle_lines_ex(cu_rect, 1, rl.Color(80, 80, 100, 255))
    rl.draw_text(f"Click Lv.{game.click_level}  ->  Lv.{game.click_level+1}", 30, cu_y + 5, 16, rl.Color(220, 220, 240, 255))
    rl.draw_text(f"Cost: {format_num(cu_cost)}", 30, cu_y + 22, 14, rl.Color(150, 150, 170, 255))

    # Right panel
    rl.draw_line(PANEL_X, 50, PANEL_X, H, rl.Color(50, 50, 70, 255))
    panel_top = 55

    visible_sources = [i for i in range(len(SOURCES)) if game.total_energy >= SOURCES[i]["unlock"] or game.levels[i] > 0]
    for i in range(len(SOURCES)):
        if i not in visible_sources:
            visible_sources.append(i)
            break

    for vi, idx in enumerate(visible_sources):
        src = SOURCES[idx]
        y = panel_top + vi * row_h
        if y + row_h < panel_top or y > H:
            continue

        unlocked = game.total_energy >= src["unlock"] or game.levels[idx] > 0
        row_rect = rl.Rectangle(PANEL_X + 5, y + 2, W - PANEL_X - 12, row_h - 4)
        bg = rl.Color(30, 30, 45, 255) if unlocked else rl.Color(25, 25, 35, 180)
        rl.draw_rectangle_rec(row_rect, bg)
        accent = src["color"] if unlocked else rl.Color(60, 60, 60, 255)
        rl.draw_rectangle(PANEL_X + 5, y + 2, 4, row_h - 4, accent)
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
            cost = game.cost(idx)
            can_afford = game.energy >= cost
            bw, bh = 100, 28
            bx = W - bw - 18
            by = y + (row_h - bh) // 2
            btn_rect = rl.Rectangle(bx, by, bw, bh)
            btn_col = rl.Color(40, 100, 90, 255) if can_afford else rl.Color(40, 40, 50, 255)
            rl.draw_rectangle_rec(btn_rect, btn_col)
            rl.draw_rectangle_lines_ex(btn_rect, 1, rl.Color(80, 80, 100, 255))
            label = f"Buy {format_num(cost)}"
            rl.draw_text(label, bx + 6, by + 7, 14, rl.Color(200, 200, 220, 255))


def main():
    rl.init_window(W, H, "Screenshot")
    rl.set_target_fps(60)

    # Warmup frames (double buffering needs a few frames)
    for _ in range(3):
        rl.begin_drawing()
        rl.clear_background(rl.Color(18, 18, 28, 255))
        rl.end_drawing()

    # Screenshot 1: Early game
    game1 = Game()
    game1.energy = 45
    game1.total_energy = 85
    game1.levels[0] = 3  # Coal Lv.3
    game1.click_level = 2
    game1.click_power = 1.5

    for _ in range(3):
        rl.begin_drawing()
        draw_game(game1)
        rl.end_drawing()
    rl.take_screenshot("early_game.png")

    # Screenshot 2: Mid/late game
    game2 = Game()
    game2.energy = 125000
    game2.total_energy = 450000
    game2.levels[0] = 15  # Coal
    game2.levels[1] = 12  # Oil
    game2.levels[2] = 8   # Gas
    game2.levels[3] = 5   # Solar
    game2.levels[4] = 3   # Wind
    game2.levels[5] = 2   # Hydro
    game2.click_level = 8
    game2.click_power = 1.0 + 7 * 0.5

    for _ in range(3):
        rl.begin_drawing()
        draw_game(game2)
        rl.end_drawing()
    rl.take_screenshot("mid_game.png")

    rl.close_window()
    print("Screenshots saved!")


if __name__ == "__main__":
    main()
