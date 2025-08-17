from dataclasses import dataclass, asdict
import math
from typing import Tuple


@dataclass
class GameObject:
    """Base class for all game objects with position and collision detection."""
    x: float
    y: float
    radius: float
    color: Tuple[int, int, int]
    object_type: str = "GameObject"

    def is_colliding(self, other: 'GameObject') -> bool:
        """Check if this object is colliding with another game object."""
        distance = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
        # Account for score if the object has one (e.g., Player)
        self_effective_radius = self.radius + (self.score if hasattr(self, 'score') else 0)
        other_effective_radius = other.radius + (other.score if hasattr(other, 'score') else 0)
        
        return distance <= self_effective_radius + other_effective_radius

    def distance_to(self, other: 'GameObject') -> float:
        """Calculate distance to another game object."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def to_dict(self):
        """Return a dictionary representation of the GameObject object."""
        return asdict(self)
    
    def __str__(self):
        """Returns a formatted string describing the GameObject object's core attributes."""
        return f"{self.object_type}(x={self.x}, y={self.y}, radius={self.radius}, color={self.color})"
    
    def __repr__(self):
        """Returns a string representation of the GameObject object."""
        return str(self)