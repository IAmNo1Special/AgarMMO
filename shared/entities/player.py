import random
import time
import math

from shared.entities.survival import SurvivalStats, SurvivalSystem
from shared.entities.skills.push import PushSkill
from shared.entities.skills.pull import PullSkill
from shared.utils.config_loader import player_cfg


class Player:
    def __init__(self, player_id, name, x=0, y=0):
        self.id = player_id
        self.name = name
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
            'push': PushSkill(),
            'pull': PullSkill()
        }
        self.push_skill_active = False
        self.push_skill_end_time = 0
        self.pull_skill_active = False
        self.pull_skill_end_time = 0
        
        # Age and growth tracking
        self.birth_time = time.time()
        self.age = 0  # in seconds
        self.radius = player_cfg['size']['newborn']  # Start at newborn size

    def __str__(self):
        return f"Player(id={self.id}, name='{self.name}', score={self.score}, x={self.x}, y={self.y})"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        # Calculate growth percentage (0-100)
        growth_pct = min(100.0, (self.age / player_cfg['size']['growth_duration']) * 100)
        
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "score": self.score,
            "color": self.color,
            "age": self.age,
            "growth_percentage": growth_pct,
            "push_skill_active": self.push_skill_active,
            "push_radius": getattr(self, 'push_radius', 0),
            "pull_skill_active": self.pull_skill_active,
            "pull_radius": getattr(self, 'pull_radius', 0),
        }

    def update(self, dt):
        """Update player state, including age and size.
        
        The player's radius is determined purely by their age, growing from 'newborn' size
        to 'adult' size over the configured growth duration.
        """
        # Update age
        self.age = time.time() - self.birth_time
        
        # Calculate size based purely on age
        # Linear interpolation between newborn and adult size based on age
        growth_progress = min(self.age / player_cfg['size']['growth_duration'], 1.0)  # Clamp at 1.0 (100%)
        self.radius = player_cfg['size']['newborn'] + \
                     (player_cfg['size']['adult'] - player_cfg['size']['newborn']) * growth_progress

    def move(self, dx, dy, world_w, world_h, padding):
        """Move the player and enforce world boundaries."""
        new_x = self.x + dx * self.start_velocity
        new_y = self.y + dy * self.start_velocity
        
        # Enforce world boundaries using current radius
        self.x = max(padding + self.radius, min(new_x, world_w - padding - self.radius))
        self.y = max(padding + self.radius, min(new_y, world_h - padding - self.radius))

    def increase_score(self, amount):
        """Increase the player's score."""
        self.score += amount

    def is_colliding(self, other, require_complete_overlap=True):
        """Check for collision with another object.
        
        Args:
            other: The other object to check collision with
            require_complete_overlap: If True, returns True only if this object is completely inside the other
        """
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if require_complete_overlap:
            # For complete overlap, the distance between centers plus the smaller radius
            # must be less than the larger radius
            if self.radius > other.radius:
                return distance + other.radius <= self.radius
            else:
                return distance + self.radius <= other.radius
        return distance < self.radius + other.radius