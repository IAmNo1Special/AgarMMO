# Player Class

The `Player` class represents a player in the AgarMMO game, extending the base `GameObject` class to manage player state, skills, and interactions.

## Class Definition

```python
class Player(GameObject):
    """
    Represents a player in the game with movement, skills, and survival mechanics.
    
    Attributes:
        id (int): Unique player identifier
        name (str): Player's display name
        score (float): Player's current score
        color (Tuple[int, int, int]): Player's RGB color
        radius (float): Current size of the player
        is_moving (bool): Whether player is currently moving
        is_sprinting (bool): Whether sprint mode is active
        is_crafting (bool): Whether player is crafting
        skills (Dict[str, Skill]): Available skills
        stats (SurvivalStats): Player's survival statistics
        birth_time (float): Timestamp when player was created
        age (float): Player's age in seconds
    """
    
    def __init__(self, player_id: int, name: str, x: float = 0, y: float = 0):
        """
        Initialize a new player instance.
        
        Args:
            player_id: Unique identifier for the player
            name: Player's display name
            x: Initial x-coordinate (default: 0)
            y: Initial y-coordinate (default: 0)
        """
        # Initialize base GameObject
        config = ConfigLoader.load_config('player.yaml')
        radius = config.get('initial_radius', 20)
        color = self._generate_random_color()
        super().__init__(x, y, radius, color, object_type="Player")
        
        self.id = player_id
        self.name = name
        self.score = 0
        self.is_moving = False
        self.is_sprinting = False
        self.is_crafting = False
        self.push_skill_active = False
        self.pull_skill_active = False
        self.skills = self._initialize_skills()
        self.birth_time = time.time()
        self.age = 0
        self._survival = SurvivalSystem()
        self.stats = self._survival.stats
```

## Initialization

The Player class is initialized with:

- A unique player ID
- A display name
- Optional starting coordinates (x, y)

Default values are loaded from the game's configuration system.

## Core Methods

### Movement

#### `move(dx: float, dy: float, dt: float) -> None`

Updates the player's position based on input direction and elapsed time.

**Parameters:**

- `dx`: Normalized x-axis movement direction (-1.0 to 1.0)
- `dy`: Normalized y-axis movement direction (-1.0 to 1.0)
- `dt`: Time elapsed since last update (in seconds)

**Example:**

```python
# Move player right at half speed
player.move(0.5, 0, 1/60)
```

### Skills

#### `activate_skill(skill_name: str) -> bool`

Activates the specified skill if available and not on cooldown.

**Parameters:**

- `skill_name`: Name of the skill to activate ('push' or 'pull')

**Returns:**

- `bool`: True if skill was activated, False otherwise

**Example:**

```python
if player.activate_skill('push'):
    print("Push skill activated!")
```

### Score Management

#### `increase_score(amount: float) -> None`

Increases the player's score and updates their size accordingly.

**Parameters:**

- `amount`: Points to add to the score

**Example:**

```python
player.increase_score(100)  # Add 100 points
```

### State Management

#### `update(dt: float) -> None`

Updates the player's internal state, including:

- Age calculation
- Skill cooldowns
- Survival mechanics
- Size based on score

**Parameters:**

- `dt`: Time elapsed since last update (in seconds)

### Serialization

#### `to_dict() -> Dict[str, Any]`

Converts the player's state to a dictionary for network transmission.

**Returns:**

- `Dict[str, Any]`: Dictionary containing player's state

**Example:**

```python
player_data = player.to_dict()
# {'id': 1, 'name': 'Player1', 'x': 100.0, 'y': 150.0, 'score': 0, ...}
```

## Growth Mechanics

Players grow in size based on their score according to the formula:

```python
radius = base_radius + (score * growth_factor) ^ growth_exponent
```

**Configuration (player.yaml):**

```yaml
initial_radius: 20
max_radius: 200
growth_factor: 0.1
growth_exponent: 0.5
```

## Skills System

### Available Skills

#### Push

- **Effect**: Repels nearby objects
- **Cooldown**: 10 seconds
- **Duration**: 2 seconds
- **Range**: Scales with player size

#### Pull

- **Effect**: Attracts nearby objects
- **Cooldown**: 15 seconds
- **Duration**: 3 seconds
- **Range**: Scales with player size

## Survival System

Players must manage their survival stats which affect gameplay:

| Stat      | Effect When Low | Recovery Method |
|-----------|------------------|------------------|
| Health    | Player dies      | Eating food      |
| Hunger    | Health decreases | Eating food      |
| Stamina   | Cannot sprint    | Resting          |

## Thread Safety

- The Player class is not thread-safe
- External synchronization is required when accessed from multiple threads
- Network operations should be handled through the game's networking layer

## Performance Considerations

- Player updates are called every frame - keep the update method efficient
- Collision detection uses spatial partitioning for optimization
- Skill effects use object pooling where possible

## Dependencies

### Standard Library

- `time`: For tracking player age and skill timers
- `math`: For movement and collision calculations
- `random`: For color generation
- `typing`: For type hints

### Project Modules

- `shared.entities.game_object`: Base class inheritance
- `shared.entities.skills.push`: Push skill implementation
- `shared.entities.skills.pull`: Pull skill implementation
- `shared.entities.survival`: Survival mechanics
- `shared.utils.config_loader`: Game configuration

## Related Classes

- `GameObject`: Base class for all game objects
- `Food`: Consumable items that affect player stats
- `Skill`: Base class for player abilities
