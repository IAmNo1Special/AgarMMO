from typing import Tuple
from dataclasses import dataclass, asdict
import random

from shared.entities.game_object import GameObject
from shared.utils.config_loader import food_cfg

@dataclass
class Food(GameObject):
    """Represents a food item in the game."""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = None):
        if color is None:
            color = random.choice(food_cfg['colors'])
        super().__init__(x, y, food_cfg['radius'], color, "Food")
    
    def to_dict(self):
        """Return a dictionary representation of the Food object."""
        return asdict(self)

    def __str__(self):
        """Returns a formatted string describing the Food object's core attributes."""
        return f"{self.object_type}(x={self.x}, y={self.y}, radius={self.radius}, color={self.color})"
    
    def __repr__(self):
        """Returns a string representation of the Food object."""
        return str(self)