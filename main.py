import pyray as rl
import math
import time

# --- Game Data ---

SOURCES = [
    {"name": "Coal Plant",       "base_cost": 10,     "base_eps": 1,       "pollution": 10,  "unlock": 0,       "color": rl.Color(80, 80, 80, 255)},
    {"name": "Oil Rig",          "base_cost": 100,    "base_eps": 5,       "pollution": 8,   "unlock": 50,      "color": rl.Color(40, 40, 40, 255)},
    {"name": "Natural Gas",      "base_cost": 500,    "base_eps": 20,      "pollution": 5,   "unlock": 300,     "color": rl.Color(100, 140, 180, 255)},
    {"name": "Solar Farm",       "base_cost": 2000,   "base_eps": 60,      "pollution": 1,   "unlock": 1500,    "color": rl.Color(255, 200, 50, 255)},
    {"name": "Wind Turbine",     "base_cost": 8000,   "base_eps": 150,     "pollution": 1,   "unlock": 6000,    "color": rl.Color(180, 220, 255, 255)},
    {"name": "Hydroelectric",    "base_cost": 30000,  "base_eps": 400,     "pollution": 2,   "unlock": 25000,   "color": rl.Color(50, 120, 200, 255)},
    {"name": "Nuclear Fission",  "base_cost": 100000, "base_eps": 1200,    "pollution": 3,   "unlock": 80000,   "color": rl.Color(0, 200, 100, 255)},
    {"name": "Nuclear Fusion",   "base_cost": 500000, "base_eps": 5000,    "pollution": 0,   "unlock": 400000,  "color": rl.Color(0, 255, 220, 255)},
]

class Game:
    def __init__(self):
        self.energy = 0.0
        self.total_energy = 0.0
        self.click_power = 1.0
        self.click_level = 1
        self.levels = [0] * len(SOURCES)
        self.click_anim = 0.0
        self.particles = []
        self.flash_alpha = 0

    def cost(self, idx):
        return int(SOURCES[idx]["base_cost"] * (1.15 ** self.levels[idx]))

    def eps(self, idx):
        return SOURCES[idx]["base_eps"] * self.levels[idx]

    def total_eps(self):
        return sum(self.eps(i) for i in range(len(SOURCES)))

    def pollution(self):
        total_prod = self.total_eps()
        if total_prod == 0:
            return 0
        weighted = sum(SOURCES[i]["pollution"] * self.eps(i) for i in range(len(SOURCES)))
        return weighted / total_prod

    def click_upgrade_cost(self):
        return int(20 * (1.5 ** (self.click_level - 1)))

    def buy(self, idx):
        c = self.cost(idx)
        if self.energy >= c:
            self.energy -= c
            self.levels[idx] += 1
            return True
        return False

    def upgrade_click(self):
        c = self.click_upgrade_cost()
        if self.energy >= c:
            self.energy -= c
            self.click_level += 1
            self.click_power = 1.0 + (self.click_level - 1) * 0.5
            return True
        return False

    def do_click(self):
        gained = self.click_power
        self.energy += gained
        self.total_energy += gained
        self.click_anim = 1.0
        self.flash_alpha = 60
        for _ in range(5):
            angle = rl.get_random_value(0, 360) * math.pi / 180
            speed = rl.get_random_value(80, 200)
            self.particles.append({
                "x": 0.0, "y": 0.0,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": 0.6,
            })
        return gained

    def update(self, dt):
        eps = self.total_eps()
        gained = eps * dt
        self.energy += gained
        self.total_energy += gained
        if self.click_anim > 0:
            self.click_anim = max(0, self.click_anim - dt * 4)
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - dt * 200)
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]


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
    # 0 = green, 10 = red
    t = min(p / 10.0, 1.0)
    r = int(40 + 200 * t)
    g = int(200 * (1 - t) + 40)
    return rl.Color(r, g, 40, 255)


def main():
    W, H = 900, 650
    rl.init_window(W, H, "Energy Clicker")
    rl.set_target_fps(60)

    game = Game()

    PANEL_X = 340
    BUTTON_CX = 160
    BUTTON_CY = 340
    BUTTON_R = 100

    scroll_offset = 0
    row_h = 72

    while not rl.window_should_close():
        dt = rl.get_frame_time()
        game.update(dt)
        mx, my = rl.get_mouse_x(), rl.get_mouse_y()

        # --- Input ---
        clicked_button = False
        if rl.is_mouse_button_pressed(0):
            dx = mx - BUTTON_CX
            dy = my - BUTTON_CY
            if dx * dx + dy * dy <= BUTTON_R * BUTTON_R:
                clicked_button = True
                game.do_click()

        # scroll in panel
        if mx > PANEL_X:
            scroll_offset -= rl.get_mouse_wheel_move() * 30

        visible_sources = [i for i in range(len(SOURCES)) if game.total_energy >= SOURCES[i]["unlock"] or game.levels[i] > 0]
        # include next locked one as teaser
        for i in range(len(SOURCES)):
            if i not in visible_sources:
                visible_sources.append(i)
                break
        max_scroll = max(0, len(visible_sources) * row_h - (H - 160))
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        # --- Draw ---
        rl.begin_drawing()
        rl.clear_background(rl.Color(18, 18, 28, 255))

        # Header bar
        rl.draw_rectangle(0, 0, W, 50, rl.Color(25, 25, 40, 255))
        rl.draw_text(f"Energy: {format_num(game.energy)}", 15, 12, 24, rl.Color(0, 230, 180, 255))
        eps = game.total_eps()
        rl.draw_text(f"{format_num(eps)}/s", 280, 16, 18, rl.Color(150, 150, 180, 255))

        # Pollution meter
        poll = game.pollution()
        pc = pollution_color(poll)
        poll_label = "Pollution"
        if poll == 0 and eps > 0:
            poll_label = "Clean!"
        rl.draw_text(f"{poll_label}: {poll:.1f}", W - 220, 8, 18, pc)
        bar_x, bar_y, bar_w, bar_h = W - 220, 30, 180, 10
        rl.draw_rectangle(bar_x, bar_y, bar_w, bar_h, rl.Color(40, 40, 50, 255))
        fill = int(bar_w * min(poll / 10.0, 1.0))
        if fill > 0:
            rl.draw_rectangle(bar_x, bar_y, fill, bar_h, pc)

        # --- Left panel: big click button ---
        # flash
        if game.flash_alpha > 0:
            rl.draw_rectangle(0, 50, PANEL_X, H - 50, rl.Color(0, 230, 180, int(game.flash_alpha)))

        # button glow
        scale = 1.0 + 0.12 * game.click_anim
        r = int(BUTTON_R * scale)
        rl.draw_circle(BUTTON_CX, BUTTON_CY, r + 8, rl.Color(0, 180, 140, 40))
        rl.draw_circle(BUTTON_CX, BUTTON_CY, r + 4, rl.Color(0, 180, 140, 60))

        # button body
        btn_color = rl.Color(0, 200, 160, 255) if not clicked_button else rl.Color(0, 255, 200, 255)
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

        # Click upgrade button
        cu_cost = game.click_upgrade_cost()
        cu_y = H - 80
        cu_rect = rl.Rectangle(20, cu_y, PANEL_X - 50, 40)
        can_afford_cu = game.energy >= cu_cost
        cu_color = rl.Color(40, 100, 90, 255) if can_afford_cu else rl.Color(40, 40, 50, 255)
        rl.draw_rectangle_rec(cu_rect, cu_color)
        rl.draw_rectangle_lines_ex(cu_rect, 1, rl.Color(80, 80, 100, 255))
        rl.draw_text(f"Click Lv.{game.click_level}  ->  Lv.{game.click_level+1}", 30, cu_y + 5, 16, rl.Color(220, 220, 240, 255))
        rl.draw_text(f"Cost: {format_num(cu_cost)}", 30, cu_y + 22, 14, rl.Color(150, 150, 170, 255))

        if rl.is_mouse_button_pressed(0) and rl.check_collision_point_rec(rl.Vector2(mx, my), cu_rect):
            game.upgrade_click()

        # --- Right panel: energy sources ---
        rl.draw_line(PANEL_X, 50, PANEL_X, H, rl.Color(50, 50, 70, 255))

        # clip area
        panel_top = 55
        panel_h = H - panel_top - 5
        rl.begin_scissor_mode(PANEL_X + 1, panel_top, W - PANEL_X - 1, panel_h)

        for vi, idx in enumerate(visible_sources):
            src = SOURCES[idx]
            y = panel_top + vi * row_h - int(scroll_offset)
            if y + row_h < panel_top or y > H:
                continue

            unlocked = game.total_energy >= src["unlock"] or game.levels[idx] > 0
            row_rect = rl.Rectangle(PANEL_X + 5, y + 2, W - PANEL_X - 12, row_h - 4)

            # row bg
            bg = rl.Color(30, 30, 45, 255) if unlocked else rl.Color(25, 25, 35, 180)
            rl.draw_rectangle_rec(row_rect, bg)

            # color accent bar
            accent = src["color"] if unlocked else rl.Color(60, 60, 60, 255)
            rl.draw_rectangle(PANEL_X + 5, y + 2, 4, row_h - 4, accent)

            tx = PANEL_X + 16

            if not unlocked:
                rl.draw_text(f"??? (need {format_num(src['unlock'])} total energy)", tx, y + 18, 16, rl.Color(100, 100, 120, 255))
                # pollution hint
                p = src["pollution"]
                hint = "Very Dirty" if p >= 8 else "Dirty" if p >= 5 else "Moderate" if p >= 3 else "Clean" if p >= 1 else "Zero Emission"
                rl.draw_text(hint, tx, y + 40, 12, rl.Color(80, 80, 100, 255))
            else:
                # name + level
                rl.draw_text(f"{src['name']}  Lv.{game.levels[idx]}", tx, y + 6, 16, rl.Color(220, 220, 240, 255))

                # eps
                e = game.eps(idx)
                rl.draw_text(f"{format_num(e)}/s", tx, y + 26, 14, rl.Color(0, 200, 160, 255))

                # pollution
                p = src["pollution"]
                plabel = f"Pollution: {p}" if p > 0 else "Zero Emission!"
                rl.draw_text(plabel, tx + 100, y + 26, 12, pollution_color(p))

                # buy button
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

                if rl.is_mouse_button_pressed(0) and rl.check_collision_point_rec(rl.Vector2(mx, my), btn_rect):
                    game.buy(idx)

        rl.end_scissor_mode()

        rl.end_drawing()

    rl.close_window()


if __name__ == "__main__":
    main()
