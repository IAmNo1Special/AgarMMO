# Game Module

The `game.py` module serves as the core game client, managing the game loop, rendering, and server communication.

## Class: `Game`

Main game class that orchestrates the game loop, rendering, and network communication.

### Initialization

```python
def __init__(self):
    """Initialize the game client with default settings and load configuration."""
```

### Attributes

- `config` (dict): Loaded game configuration
- `screen`: Pygame display surface
- `clock`: Pygame clock for frame rate control
- `network`: Network manager instance
- `game_renderer`: Handles game object rendering
- `ui_renderer`: Manages UI elements
- `input_handler`: Processes user input
- `player_id`: Unique identifier from server
- `game_state`: Current game state from server

### Methods

#### `load_config()`

Loads game configuration from YAML files.

**Returns:**

- `dict`: Loaded configuration

#### `init_window()`

Initializes the game window with specified settings.

#### `connect_to_server(name: str) -> bool`

Establishes connection to the game server.

**Parameters:**

- `name` (str): Player's display name

**Returns:**

- `bool`: `True` if connection was successful

#### `get_game_state()`

Fetches and updates the current game state from server.

#### `draw()`

Renders the current game state.

#### `run(player_name: str)`

Main game loop.

**Parameters:**

- `player_name` (str): Player's display name

## Game Loop Responsibilities

- Manages frame timing and updates
- Handles server communication
- Updates game state
- Renders game objects and UI
- Processes user input

## Configuration

Configuration is loaded from YAML files with the following structure:

- `screen`: Display settings (width, height, title)
- `player`: Player settings (size, speed)
- `rendering`: Visual settings (colors, fonts)
- `game`: Core game mechanics

## Dependencies

- `pygame`: For window management and rendering
- `shared.utils.config_loader`: For game configuration
- `client.network`: For server communication
- `client.rendering`: For game and UI rendering
- `client.input_handler`: For processing user input
