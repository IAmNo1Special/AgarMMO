# Game Manager Module

The `game_manager.py` module manages the core game logic, including game state, collisions, scoring, and player interactions.

## Class: `GameManager`

Manages the game state and implements core game mechanics.

### Initialization

```python
def __init__(self, players: Dict[int, Player], balls: List[Food], 
             world_dimensions: Tuple[int, int], player_start_radius: int, 
             player_colors: List[Tuple[int, int, int]], lock: RLock, 
             start: bool, start_time: float):
    """
    Initialize the game manager with initial game state.
    
    Args:
        players: Dictionary of player_id -> Player objects
        balls: List of food items in the game
        world_dimensions: Tuple of (width, height) for the game world
        player_start_radius: Initial radius for new players
        player_colors: List of available player colors
        lock: Threading lock for thread safety
        start: Whether the game has started
        start_time: Game start timestamp
    """
```

### Attributes

- `players` (Dict[int, Player]): Active players by ID
- `balls` (List[Food]): List of food items in the game
- `world_width` (int): World width in pixels
- `world_height` (int): World height in pixels
- `player_start_radius` (int): Initial radius for new players
- `player_colors` (List[Tuple[int, int, int]]): Available player colors
- `lock` (RLock): Thread synchronization lock
- `game_started` (bool): Whether the game has started
- `start_time` (float): Game start timestamp
- `config` (dict): Loaded game configuration

### Methods

#### `check_collision(players: Dict[int, Player], balls: List[Food]) -> None`

Checks for collisions between players and food items.

**Parameters:**

- `players`: Dictionary of player_id -> Player objects
- `balls`: List of food items in the game

#### `handle_player_collisions(players: Dict[int, Player]) -> None`

Handles collisions between players.

**Parameters:**

- `players`: Dictionary of player_id -> Player objects

#### `respawn_player(player_id: int, players: Dict[int, Player]) -> None`

Respawns a player after death.

**Parameters:**

- `player_id`: ID of the player to respawn
- `players`: Dictionary of player_id -> Player objects

#### `update_game_state(players: Dict[int, Player], balls: List[Food]) -> None`

Updates the game state for all entities.

**Parameters:**

- `players`: Dictionary of player_id -> Player objects
- `balls`: List of food items in the game

#### `get_game_state(players: Dict[int, Player], balls: List[Food]) -> Dict`

Returns the current game state.

**Parameters:**

- `players`: Dictionary of player_id -> Player objects
- `balls`: List of food items in the game

**Returns:**

- `Dict`: Current game state

## Game Mechanics

### Food System

- Manages food item spawning and respawning
- Handles food consumption by players
- Implements food distribution in the game world
- Configurable food spawn rates and limits

### Player System

- Tracks player states (alive/dead)
- Manages player growth and scoring
- Implements player collision detection
- Handles player respawning with cooldown
- Manages player leaderboard and rankings

### World Management

- Maintains world boundaries and constraints
- Handles object positioning and collision detection
- Manages game time and state transitions
- Implements world persistence (if configured)

## Thread Safety

- Uses `RLock` for thread-safe operations
- Implements proper locking for shared resources
- Handles concurrent access to game state
- Manages thread lifecycles and cleanup

## Configuration

Loaded from YAML configuration files:

- `server_cfg`: Server-specific settings
- `world_cfg`: World dimensions and boundaries
- `game_cfg`: Game mechanics configuration
- `food_cfg`: Food spawning and behavior
- `skills_cfg`: Player abilities and skills

## Dependencies

### Standard Library

- `random`: For random number generation
- `math`: For geometric calculations
- `threading`: For thread synchronization
- `logging`: For game event logging
- `time`: For timing operations

### Project Modules

- `shared.entities.player`: Player class definition
- `shared.entities.food`: Food class definition
- `shared.utils.config_loader`: Game configuration
- `shared.utils.helpers`: Utility functions

## Performance Considerations

- Implements spatial partitioning for collision detection
- Uses efficient data structures for game state
- Minimizes memory allocations during updates
- Optimizes network bandwidth usage
