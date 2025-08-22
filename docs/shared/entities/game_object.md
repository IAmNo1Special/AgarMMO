# GameObject Class

The `GameObject` class is the base class for all game objects in the AgarMMO game. It provides core functionality for position tracking, collision detection, and basic game object properties.

## Class Definition

```python
class GameObject:
    """
    Base class for all game objects with position and collision detection.
    
    Attributes:
        x (float): The x-coordinate of the object's center
        y (float): The y-coordinate of the object's center
        radius (float): The collision radius of the object
        color (Tuple[int, int, int]): The RGB color of the object
        object_type (str): A string identifier for the object type (default: "GameObject")
    """
    x: float
    y: float
    radius: float
    color: Tuple[int, int, int]
    object_type: str = "GameObject"

    def __init__(self, x: float, y: float, radius: float, color: Tuple[int, int, int], 
                 object_type: str = "GameObject"):
        """
        Initialize a new game object.
        
        Args:
            x: X-coordinate of the object's center
            y: Y-coordinate of the object's center
            radius: Collision radius of the object
            color: RGB color tuple (0-255, 0-255, 0-255)
            object_type: Type identifier for the object
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.object_type = object_type
```

## Methods

### Collision Detection

#### `is_colliding(other: 'GameObject') -> bool`

Checks if this object is colliding with another game object using circular collision detection.

**Parameters:**

- `other` (GameObject): The other game object to check collision with

**Returns:**

- `bool`: True if the objects are colliding, False otherwise

**Example:**

```python
if player.is_colliding(food):
    player.eat(food)
```

### Distance Calculation

#### `distance_to(other: 'GameObject') -> float`

Calculates the Euclidean distance to another game object.

**Parameters:**

- `other` (GameObject): The target game object

**Returns:**

- `float`: The distance between the centers of the two objects

**Example:**

```python
distance = player.distance_to(nearest_food)
```

### Serialization

#### `to_dict() -> Dict[str, Any]`

Converts the game object to a dictionary representation suitable for serialization.

**Returns:**

- `Dict[str, Any]`: A dictionary containing all object attributes

**Example:**

```python
data = player.to_dict()
# Output: {'x': 100.0, 'y': 150.0, 'radius': 20.0, 'color': (255, 0, 0), 'object_type': 'Player'}
```

### String Representation

#### `__str__() -> str`

Returns a human-readable string representation of the object.

**Returns:**

- `str`: Formatted string with object attributes

**Example:**

```python
print(str(player))
# Output: GameObject(x=100.0, y=150.0, radius=20.0, color=(255, 0, 0), type=Player)
```

#### `__repr__() -> str`

Returns the string representation of the object (same as `__str__`).

**Returns:**

- `str`: String representation of the object

## Inheritance

This class is designed to be inherited by other game object types. Child classes should:

1. Call `super().__init__()` with appropriate parameters
2. Override `object_type` with a unique identifier
3. Extend functionality as needed

### Example Implementation

```python
class Player(GameObject):
    def __init__(self, x: float, y: float, radius: float, color: Tuple[int, int, int], name: str):
        super().__init__(x, y, radius, color, object_type="Player")
        self.name = name
        self.score = 0

    def update(self, dx: float, dy: float):
        """Update player position based on input."""
        self.x += dx
        self.y += dy
```

## Thread Safety

This class is not thread-safe by itself. When used in a multi-threaded context:

- External synchronization is required
- Consider using `threading.Lock` for shared access
- Be aware of the GIL in CPython

## Performance Considerations

- Collision detection uses simple distance comparison (O(1) per check)
- For large numbers of objects, consider spatial partitioning
- Object creation/destruction should be minimized in performance-critical paths

## Dependencies

### Standard Library

- `math`: For distance calculations
- `typing`: For type hints
- `dataclasses`: For automatic method generation (if using @dataclass)

### Project Modules

- None (base class has no project-specific dependencies)

## Related Classes

- `Player`: Represents a player-controlled entity
- `Food`: Represents consumable food items
- `Skill`: Base class for player abilities
