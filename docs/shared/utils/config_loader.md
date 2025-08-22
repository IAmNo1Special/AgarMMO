# Configuration Loader

## Module: `config_loader.py`

```python
class ConfigLoader:
    """
    Utility class for loading and managing YAML configuration files.
    
    This class provides a simple interface for loading YAML configuration files
    from the game's config directory. It includes caching to avoid repeated
    file system operations.
    """
    _config_cache = {}
    
    @classmethod
    def load_config(cls, config_name: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file from the config directory.
        
        Args:
            config_name: Name of the configuration file (without .yaml extension)
            
        Returns:
            Dictionary containing the parsed configuration data
            
        Raises:
            FileNotFoundError: If the specified configuration file does not exist
            yaml.YAMLError: If there is an error parsing the YAML file
            
        Example:
            ```python
            # Load the game configuration
            game_config = ConfigLoader.load_config('game')
            
            # Access configuration values
            max_players = game_config['max_players']
            ```
        """
        if config_name in cls._config_cache:
            return cls._config_cache[config_name]
            
        config_path = Path('config') / f"{config_name}.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        cls._config_cache[config_name] = config
        return config
```

## Core Functionality

### `load_config(config_name: str) -> Dict[str, Any]`

Loads and parses a YAML configuration file from the config directory.

**Parameters:**

- `config_name`: Name of the configuration file (without .yaml extension)

**Returns:**

- `Dict[str, Any]`: Dictionary containing the parsed configuration data

**Raises:**

- `FileNotFoundError`: If the specified configuration file does not exist
- `yaml.YAMLError`: If there is an error parsing the YAML file

## Usage Example

```python
from shared.utils.config_loader import ConfigLoader

# Load a configuration file
try:
    game_config = ConfigLoader.load_config('game')
    food_config = ConfigLoader.load_config('food')
    
    # Access configuration values
    max_players = game_config['max_players']
    food_spawn_rate = food_config['spawn_rate']
    
except FileNotFoundError as e:
    print(f"Configuration file not found: {e}")
except yaml.YAMLError as e:
    print(f"Error parsing configuration: {e}")
```

## Configuration File Format

Configuration files should be in YAML format. Example `game.yaml`:

```yaml
# Core game settings
game:
  max_players: 100
  world_size: 5000
  tick_rate: 60
  
# Player settings
player:
  initial_radius: 20
  max_radius: 500
  speed: 5.0
  
# Food settings
food:
  initial_count: 100
  max_count: 1000
  spawn_rate: 0.5  # per second
```

## Performance Considerations

- Configuration files are cached in memory after first load
- File I/O only occurs when a configuration is first accessed
- Uses `yaml.safe_load` for security
- Thread-safe for concurrent access (due to GIL in CPython)

## Dependencies

### Standard Library

- `pathlib.Path`: For cross-platform path handling

### Third-Party

- `PyYAML`: For YAML parsing

## Related Modules

- `shared.entities.game_object`: Uses configuration for game object properties
- `server.game_manager`: Loads game configuration on server start
- `client.rendering.game_renderer`: Uses configuration for rendering parameters
- `network_cfg`: Network-related settings
- `player_cfg`: Player attributes and settings
- `server_cfg`: Server configuration
- `skills_cfg`: Skills and abilities configuration
- `survival_cfg`: Survival mechanics configuration
- `world_cfg`: World generation and settings
