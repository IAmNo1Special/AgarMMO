# shared/survival.py
from dataclasses import dataclass, asdict

from utils.config_loader import survival_cfg

@dataclass
class SurvivalStats:
    health: float = 100.0
    calories: float = 3000.0
    hydration: float = 5000.0
    blood: float = 5000.0
    bleeding: bool = False
    infection: bool = False
    temperature: float = 37.0   # Celsius

    def clamp(self):
        self.health = max(0.0, min(self.health, survival_cfg['max_health']))
        self.calories = max(0.0, min(self.calories, survival_cfg['max_calories']))
        self.hydration = max(0.0, min(self.hydration, survival_cfg['max_hydration']))
        self.blood = max(0.0, min(self.blood, survival_cfg['max_blood']))

    def serialize(self):
        return asdict(self)

class SurvivalSystem:
    """
    Server-authoritative survival logic. Call update() once per second (or at a fixed step).
    """
    def __init__(self):
        self.cfg = survival_cfg

    def update(self, stats: SurvivalStats, dt: float, *, moving=False, sprinting=False, crafting=False):
        c = self.cfg

        # ===== base drains =====
        cal_drain = c['calories_drain_idle']
        hyd_drain = c['hydration_drain_idle']

        # activity multipliers (server decides)
        mult = 1.0
        if moving:   mult *= c['move_mult']
        if sprinting: mult *= c['sprint_mult']
        if crafting: mult *= c['crafting_mult']

        stats.calories -= cal_drain * mult * dt
        stats.hydration -= hyd_drain * mult * dt

        # ===== starvation / dehydration penalties =====
        if stats.calories <= 0.0:
            stats.health -= c['starve_hp_loss'] * dt

        if stats.hydration <= 0.0:
            stats.health -= c['dehydrate_hp_loss'] * dt

        # ===== bleeding & blood effects =====
        if stats.bleeding:
            stats.blood -= c['bleed_loss_per_sec'] * dt
        if stats.blood < 3000.0:  # low blood pressure → hp loss
            stats.health -= c['low_blood_hp_loss'] * dt

        # ===== infection =====
        if stats.infection:
            stats.health -= c['infection_hp_loss'] * dt

        # ===== temperature =====
        if stats.temperature < c['hypothermia_f']:
            stats.health -= c['hypothermia_hp_loss'] * dt
        elif stats.temperature > c['heatstroke_f']:
            stats.hydration -= c['heatstroke_hydration_bonus_drain'] * dt

        # ===== clamp =====
        stats.clamp()

    # Server-side actions
    def eat(self, stats: SurvivalStats, kcal: float):
        stats.calories += max(0.0, kcal)
        stats.clamp()

    def drink(self, stats: SurvivalStats, amount: float):
        stats.hydration += max(0.0, amount)
        stats.clamp()

    def take_damage(self, stats: SurvivalStats, hp: float, *, cause: str = "generic"):
        stats.health -= max(0.0, hp)
        stats.clamp()

    def set_bleeding(self, stats: SurvivalStats, on: bool = True):
        stats.bleeding = on

    def bandage(self, stats: SurvivalStats):
        stats.bleeding = False

    def transfuse(self, stats: SurvivalStats, amount: float):
        stats.blood += max(0.0, amount)
        stats.clamp()

    def set_infection(self, stats: SurvivalStats, on: bool = True):
        stats.infection = on

    def set_temperature(self, stats: SurvivalStats, temp_f: float):
        stats.temperature = temp_f
