import json
import math
import os
import random


def load_sources():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sources.json")
    with open(path) as f:
        raw = json.load(f)
    for src in raw:
        src["color"] = tuple(src["color"])
    return raw


SOURCES = load_sources()


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
            angle = random.randint(0, 360) * math.pi / 180
            speed = random.randint(80, 200)
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
