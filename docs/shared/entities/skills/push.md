# Push Skill

The `PushSkill` class implements a pushing ability that allows players to repel nearby objects in the game world.

## Class Definition

```python
class PushSkill:
    """
    Implements a push skill that repels nearby objects away from the player.
    
    Attributes:
        level (int): Current skill level (default: 1)
        base_radius (float): Base radius of the push effect
        radius_per_level (float): Additional radius per skill level
        push_force (float): Strength of the push effect
        duration (float): Duration of the push effect in seconds
        cooldown (float): Time before skill can be used again
        is_active (bool): Whether the skill is currently active
        last_used (float): Timestamp when skill was last used
    """
    
    def __init__(self, level: int = 1):
        """
        Initialize a new push skill instance.
        
        Args:
            level: Initial skill level (default: 1)
        """
        self.level = level
        config = ConfigLoader.load_config('skills.yaml')['push_skill']
        self.base_radius = config['base_radius']
        self.radius_per_level = config['radius_per_level']
        self.push_force = config['push_force']
        self.duration = config['duration']
        self.cooldown = config['cooldown']
        self.is_active = False
        self.last_used = 0
        self._activation_time = 0
```

## Initialization

The PushSkill is initialized with:

- An optional skill level (default: 1)
- Configuration loaded from the game's skills configuration
- Default state values

## Core Methods

### `activate() -> bool`

Activates the push skill if it's not on cooldown.

**Returns:**

- `bool`: True if activation was successful, False otherwise

**Example:**

```python
if push_skill.activate():
    print("Push skill activated!")
```

### `update(dt: float) -> None`

Updates the skill's internal state.

**Parameters:**

- `dt`: Time elapsed since last update (in seconds)

### `get_effective_radius(player_radius: float) -> float`

Calculates the total push radius including the player's size.

**Parameters:**

- `player_radius`: The radius of the player using the skill

**Returns:**

- `float`: Total push radius (skill radius + player radius)

**Example:**

```python
radius = push_skill.get_effective_radius(player.radius)
```

### `apply_effect(target_pos: Tuple[float, float], player_pos: Tuple[float, float]) -> Tuple[float, float]`

Calculates the push force to apply to a target.

**Parameters:**

- `target_pos`: (x, y) position of the target
- `player_pos`: (x, y) position of the player

**Returns:**

- `Tuple[float, float]`: (dx, dy) force vector to apply to the target

## Properties

### `radius`

Returns the base skill radius without considering the player's size.

**Type:** `float`

### `time_remaining`

Returns the remaining duration of an active push effect.

**Type:** `float`

### `is_ready`

Returns whether the skill is ready to be used.

**Type:** `bool`

## Configuration

The push skill is configured in `config/skills.yaml`:

```yaml
push_skill:
  base_radius: 120.0     # Base radius of the push effect
  radius_per_level: 25.0 # Additional radius per skill level
  push_force: 8.0        # Strength of the push effect
  duration: 2.5          # How long the push effect lasts (seconds)
  cooldown: 12.0         # Cooldown between uses (seconds)
```

## Game Mechanics

### Activation

- Player activates the skill (e.g., by pressing a key)
- Skill enters active state for the configured duration
- Visual/audio effects play to indicate activation

### Effect

- Creates a circular push wave around the player
- Affects all game objects within the effective radius
- Push force is stronger closer to the player
- Force is applied away from the player's center
- Higher skill levels increase the push radius

### Cooldown

- After activation, skill enters cooldown
- Cannot be activated again until cooldown expires
- Visual indicators show cooldown status

## Performance Considerations

- Push effect calculations are performed every frame for active skills
- Uses distance-squared checks for better performance
- Caches calculations where possible
- Consider spatial partitioning for large numbers of objects

## Thread Safety

- Not thread-safe by itself
- Should be updated from the main game thread
- External synchronization required for multi-threaded access

## Dependencies

### Standard Library

- `time`: For tracking skill duration and cooldowns
- `math`: For distance and force calculations

### Project Modules

- `shared.utils.config_loader`: For loading skill configuration

## Related Classes

- `Player`: Uses the push skill
- `PullSkill`: Opposite effect skill
- `SkillManager`: Manages all player skills
