# Survival System

The survival system manages player statistics and survival mechanics, including health, hunger, thirst, bleeding, and temperature effects.

## Class: `SurvivalStats`

```python
@dataclass
class SurvivalStats:
    """
    Container for all survival-related statistics for a player.
    
    Attributes:
        health (float): Player's health points (0.0 to max_health)
        calories (float): Available energy from food (0.0 to max_calories)
        hydration (float): Hydration level (0.0 to max_hydration)
        blood (float): Blood volume in milliliters (0.0 to max_blood)
        bleeding (bool): Whether the player is currently bleeding
        infection (bool): Whether the player has an active infection
        temperature (float): Body temperature in Celsius
    """
    health: float = 100.0
    calories: float = 3000.0
    hydration: float = 5000.0
    blood: float = 5000.0
    bleeding: bool = False
    infection: bool = False
    temperature: float = 37.0
```

## Class: `SurvivalSystem`

Server-authoritative survival logic that should be updated periodically (recommended: once per second).

```python
class SurvivalSystem:
    """
    Manages the survival mechanics for players.
    
    This system handles:
    - Health regeneration and damage
    - Hunger and thirst depletion
    - Bleeding and infection
    - Temperature effects
    - Status effects and buffs/debuffs
    
    Configuration is loaded from 'survival.yaml' in the game config directory.
    """
    
    def __init__(self):
        """Initialize the survival system with default configuration."""
        self.config = ConfigLoader.load_config('survival.yaml')
        self.effects = {}
```

## Core Methods

### `update(stats: SurvivalStats, dt: float, **actions) -> None`

Updates all survival stats based on the elapsed time and player actions.

**Parameters:**

- `stats`: The SurvivalStats instance to update
- `dt`: Time elapsed since last update (in seconds)
- `actions`: Dictionary of player actions (e.g., moving, sprinting, crafting)

**Example:**

```python
survival.update(player.stats, 1.0, moving=True, sprinting=False)
```

### `eat(stats: SurvivalStats, kcal: float) -> None`

Increases the player's calorie count.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `kcal`: Number of calories to add (will be clamped to max_calories)

### `drink(stats: SurvivalStats, amount: float) -> None`

Increases the player's hydration level.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `amount`: Amount of hydration to add (in milliliters)

### `take_damage(stats: SurvivalStats, amount: float, **kwargs) -> None`

Reduces the player's health by the specified amount.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `amount`: Amount of health to subtract
- `cause`: Optional string describing the damage source
- `can_bleed`: Whether this damage can cause bleeding
- `can_infect`: Whether this damage can cause infection

### `heal(stats: SurvivalStats, amount: float) -> None`

Restores the player's health.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `amount`: Amount of health to restore

### `set_bleeding(stats: SurvivalStats, on: bool = True) -> None`

Sets the bleeding status of the player.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `on`: Whether bleeding should be enabled

### `bandage(stats: SurvivalStats) -> bool`

Attempts to stop bleeding and heal a small amount.

**Parameters:**

- `stats`: The SurvivalStats instance to modify

**Returns:**

- `bool`: True if bleeding was stopped, False if player wasn't bleeding

### `set_infection(stats: SurvivalStats, on: bool = True) -> None`

Sets the infection status of the player.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `on`: Whether infection should be enabled

### `apply_effect(effect_id: str, stats: SurvivalStats, duration: float = None) -> None`

Applies a status effect to the player.

**Parameters:**

- `effect_id`: ID of the effect to apply
- `stats`: The SurvivalStats instance to modify
- `duration`: Optional duration in seconds (uses default if None)

## Configuration

The survival system is configured in `config/survival.yaml`:

```yaml
# Base stats
max_health: 100.0
max_calories: 3000.0
max_hydration: 5000.0
max_blood: 5000.0

# Depletion rates (per game minute)
calorie_depletion_rate: 1.0      # Base calories burned per minute
hydration_depletion_rate: 2.0    # Base hydration lost per minute
sprint_multiplier: 1.5           # Multiplier when sprinting
cold_multiplier: 1.2             # Multiplier in cold environments

# Health regeneration
health_regen_rate: 0.1           # Health regenerated per second when well-fed/hydrated
min_calories_for_regen: 1000.0   # Minimum calories needed for health regen
min_hydration_for_regen: 2000.0  # Minimum hydration needed for health regen

# Bleeding

bleed_damage: 0.5                # Damage per second while bleeding
bleed_chance: 0.3                # Chance to start bleeding when taking damage

# Temperature

normal_temperature: 37.0         # Normal body temperature in Celsius
temperature_damage_threshold: 34.0  # Temperature where damage starts occurring
```

## Game Mechanics

### Health System

- Players have a health pool that can be damaged by various sources
- Health regenerates slowly when well-fed and hydrated
- Falling below 0 health results in player death

### Hunger and Thirst

- Calories are consumed by player actions (walking, running, etc.)
- Hydration decreases over time and faster when active
- Low calories/hydration reduces maximum health and movement speed

### Bleeding and Injuries

- Some damage sources can cause bleeding
- Bleeding causes continuous damage over time
- Bandages or medical items are required to stop bleeding

### Temperature Effects

- Environment affects player temperature
- Extreme temperatures cause damage over time
- Proper clothing and shelter can mitigate temperature effects

## Performance Considerations

- The survival system is designed to be lightweight
- Updates occur at a fixed interval (default: 1 second)
- Most calculations are simple arithmetic operations
- Effects system uses a dictionary for O(1) lookups

## Thread Safety

- Not thread-safe by default
- External synchronization required if accessed from multiple threads
- Consider using thread-local storage for multiplayer implementations

## Dependencies

### Standard Library

- `dataclasses`: For the `@dataclass` decorator and `asdict`
- `time`: For tracking effect durations
- `math`: For various calculations

### Project Modules

- `shared.utils.config_loader`: For loading survival configuration

## Related Classes

- `Player`: Contains the SurvivalStats instance
- `Inventory`: Manages items that affect survival stats
- `EffectsManager`: Handles status effects and buffs

## Additional Methods

### `_update_bleeding(stats: SurvivalStats, dt: float) -> None`

Updates the bleeding status and applies damage if bleeding.

**Parameters:**

- `stats`: The SurvivalStats instance to update
- `dt`: Time elapsed since last update (in seconds)

### `_update_infection(stats: SurvivalStats, dt: float) -> None`

Updates the infection status and applies effects if infected.

**Parameters:**

- `stats`: The SurvivalStats instance to update
- `dt`: Time elapsed since last update (in seconds)

### `transfuse(stats: SurvivalStats, amount: float)`

Increases the player's blood volume.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `amount`: Amount of blood to add

### `set_temperature(stats: SurvivalStats, temp_f: float)`

Sets the player's body temperature.

**Parameters:**

- `stats`: The SurvivalStats instance to modify
- `temp_f`: Temperature in Fahrenheit

## Configuration Details

The survival system is configured in the game's configuration under `survival_cfg`:

- `max_health`: Maximum health points
- `max_calories`: Maximum calorie storage
- `max_hydration`: Maximum hydration level
- `max_blood`: Maximum blood volume
- `calories_drain_idle`: Base calorie drain rate when idle
- `hydration_drain_idle`: Base hydration drain rate when idle
- `move_mult`: Movement speed multiplier for resource drain
- `sprint_mult`: Sprinting multiplier for resource drain
- `crafting_mult`: Crafting multiplier for resource drain
- `starve_hp_loss`: Health lost per second when starving
- `dehydrate_hp_loss`: Health lost per second when dehydrated
- `bleed_loss_per_sec`: Blood lost per second when bleeding
- `low_blood_hp_loss`: Health lost per second with low blood volume
- `infection_hp_loss`: Health lost per second when infected
- `hypothermia_f`: Temperature threshold for hypothermia
- `heatstroke_f`: Temperature threshold for heatstroke
- `hypothermia_hp_loss`: Health lost per second when too cold
- `heatstroke_hydration_bonus_drain`: Extra hydration lost when too hot

## Usage Example

```python
# Initialize
stats = SurvivalStats()
survival = SurvivalSystem()

# Update loop (call every second)
survival.update(stats, dt=1.0, moving=True, sprinting=False)

# Player actions
survival.eat(stats, 500)  # Eat food worth 500 calories
survival.drink(stats, 200)  # Drink water
survival.take_damage(stats, 10.0, cause="fall")
survival.set_bleeding(stats, True)  # Start bleeding
survival.bandage(stats)  # Stop bleeding
survival.transfuse(stats, 1000)  # Blood transfusion
survival.set_infection(stats, True)  # Get infected
survival.set_temperature(stats, 98.6)  # Set body temperature
```
