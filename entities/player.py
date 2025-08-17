import random
from entities.survival import SurvivalStats, SurvivalSystem
from entities.skills.push import PushSkill
from utils.config_loader import player_cfg


class Player:
    def __init__(self, player_id, name, x=0, y=0):
        self.id = player_id
        self.name = name
        self.radius = player_cfg['start_radius']
        self.start_velocity = player_cfg['start_velocity']
        self.color = random.choice(player_cfg['colors'])
        self.x = x
        self.y = y
        self.is_moving = False
        self.is_sprinting = False
        self.is_crafting = False
        self.score = 0
        self.stats = SurvivalStats()
        self._survival = SurvivalSystem()
        self.skills = {
            'push': PushSkill()
        }
        self.push_skill_active = False
        self.push_skill_end_time = 0

    def __str__(self):
        return f"Player(id={self.id}, name='{self.name}', score={self.score}, x={self.x}, y={self.y})"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "score": self.score,
            "color": self.color,
            "push_skill_active": self.push_skill_active,
        }

    def move(self, dx, dy, world_w, world_h, padding):
        """Move the player and enforce world boundaries."""
        new_x = self.x + dx * self.start_velocity
        new_y = self.y + dy * self.start_velocity
        
        # Enforce world boundaries
        radius = self.radius + self.score
        self.x = max(padding + radius, min(new_x, world_w - padding - radius))
        self.y = max(padding + radius, min(new_y, world_h - padding - radius))

    def grow(self, amount):
        """Increase the player's score."""
        self.score += amount

    def is_colliding(self, other):
        """Check for collision with another object."""
        import math
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < self.radius + self.score + other.radius