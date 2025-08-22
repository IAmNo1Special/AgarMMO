# Food Class

The `Food` class represents consumable food items in the AgarMMO game that players can collect to grow and score points.

## Class Definition

```python
class Food(GameObject):
    """
    Represents a consumable food item in the game world.
    
    Attributes:
        x (float): X-coordinate position
        y (float): Y-coordinate position
        radius (float): Size of the food (from config)
        color (Tuple[int, int, int]): RGB color value
        object_type (str): Always "Food"
        value (float): Point value when consumed (from config)
    """
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int] = None):
        """
        Initialize a new food item.
        
        Args:
            x: X-coordinate of the food item
            y: Y-coordinate of the food item
            color: Optional RGB color tuple. If None, a random color is chosen from config.
        """
        # Load configuration
        config = ConfigLoader.load_config('food.yaml')
        radius = config.get('radius', 5)
        
        # Generate random color if none provided
        if color is None:
            colors = config.get('colors', [(255, 0, 0), (0, 255, 0), (0, 0, 255)])
            color = random.choice(colors)
            
        # Initialize base GameObject
        super().__init__(x, y, radius, color, object_type="Food")
        
        # Food-specific properties
        self.value = config.get('value', 10)
```

## Initialization

The Food class is initialized with:

- Position coordinates (x, y)
- Optional color (randomly selected if not provided)

Default values are loaded from the game's configuration system.

## Core Methods

### Serialization

#### `to_dict() -> Dict[str, Any]`

Converts the food item to a dictionary for network transmission.

**Returns:**

- `Dict[str, Any]`: Dictionary containing all food properties

**Example:**

```python
food_data = food.to_dict()
# {'x': 100.0, 'y': 200.0, 'radius': 5.0, 'color': (255, 0, 0), 'object_type': 'Food', 'value': 10}
```

### String Representation

#### `__str__() -> str`

Returns a human-readable string representation of the food item.

**Returns:**

- `str`: Formatted string with food properties

**Example:**

```python
print(str(food))
# Food(x=100.0, y=200.0, radius=5.0, color=(255, 0, 0), value=10)
```

#### `__repr__() -> str`

Returns the string representation of the food item (same as `__str__`).

**Returns:**

- `str`: String representation of the food item

## Configuration

Food properties are configured in `config/food.yaml`:

```yaml
# Base radius of food items
radius: 5

# Point value when consumed
value: 10

# List of possible colors (RGB tuples)
colors:
  - [255, 0, 0]    # Red
  - [0, 255, 0]    # Green
  - [0, 0, 255]    # Blue
  - [255, 255, 0]  # Yellow
  - [255, 0, 255]  # Magenta
  - [0, 255, 255]  # Cyan

# Spawn settings
spawn:
  min_distance: 50    # Minimum distance from players
  max_count: 100      # Maximum number of food items
  respawn_rate: 1.0   # Items per second
```

## Usage Example

```python
from shared.entities.food import Food

# Create a food item with random color
food = Food(x=100, y=200)

# Create a red food item
red_food = Food(x=150, y=250, color=(255, 0, 0))

# Check if player collides with food
if player.is_colliding(food):
    player.increase_score(food.value)
    world.remove_food(food)

# Serialize for network transmission
food_data = food.to_dict()
```

## Thread Safety

- The Food class is thread-safe for read operations
- Write operations should be synchronized if accessed from multiple threads
- Food objects are typically managed by the game world which handles synchronization

## Performance Considerations

- Food items are lightweight objects
- Frequent creation/destruction is expected - consider object pooling
- Collision detection is optimized through spatial partitioning

## Dependencies

### Standard Library

- `random`: For selecting random colors when none specified
- `typing`: For type hints

### Project Modules

- `shared.entities.game_object`: Base class inheritance
- `shared.utils.config_loader`: Game configuration loading

## Related Classes

- `GameObject`: Base class for all game objects
- `Player`: Consumes food items
- `World`: Manages food spawning and cleanup
