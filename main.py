import os

import pyray as rl

from game import Game, SOURCES
from draw import W, H, PANEL_X, BUTTON_CX, BUTTON_CY, BUTTON_R, ROW_H
from draw import draw_header, draw_click_button, draw_click_upgrade, draw_source_panel


def main():
    rl.init_window(W, H, "Energy Clicker")
    rl.init_audio_device()
    rl.set_target_fps(60)

    # Load and play ambient music
    music_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ambient.mp3")
    music = rl.load_music_stream(music_path)
    rl.set_music_volume(music, 0.5)
    rl.play_music_stream(music)

    game = Game()
    scroll_offset = 0

    while not rl.window_should_close():
        rl.update_music_stream(music)
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

        if mx > PANEL_X:
            scroll_offset -= rl.get_mouse_wheel_move() * 30

        visible_sources = [i for i in range(len(SOURCES)) if game.total_energy >= SOURCES[i]["unlock"] or game.levels[i] > 0]
        for i in range(len(SOURCES)):
            if i not in visible_sources:
                visible_sources.append(i)
                break
        max_scroll = max(0, len(visible_sources) * ROW_H - (H - 160))
        scroll_offset = max(0, min(scroll_offset, max_scroll))

        # --- Draw ---
        rl.begin_drawing()
        rl.clear_background(rl.Color(18, 18, 28, 255))

        draw_header(game)
        draw_click_button(game, clicked_button)

        cu_rect = draw_click_upgrade(game)
        if rl.is_mouse_button_pressed(0) and rl.check_collision_point_rec(rl.Vector2(mx, my), cu_rect):
            game.upgrade_click()

        buy_rects = draw_source_panel(game, visible_sources, scroll_offset)
        if rl.is_mouse_button_pressed(0):
            for idx, rect in buy_rects.items():
                if rl.check_collision_point_rec(rl.Vector2(mx, my), rect):
                    game.buy(idx)

        rl.end_drawing()

    rl.unload_music_stream(music)
    rl.close_audio_device()
    rl.close_window()


if __name__ == "__main__":
    main()
