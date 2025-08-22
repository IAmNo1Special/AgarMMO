# Input Handler

The `input_handler.py` module processes user input and translates it into game actions and movement.

## Class: `InputHandler`

Handles all user input including keyboard and mouse events, and manages player movement.

### Initialization

```python
def __init__(self, current_id: str, players: Dict[str, Any], server: Any, 
             W: int, H: int, PLAYER_RADIUS: int, START_VEL: int)
```

### Attributes

- `current_id` (str): ID of the current player
- `players` (Dict[str, Any]): Dictionary of all players
- `server`: Network server instance
- `W` (int): Screen width
- `H` (int): Screen height
- `PLAYER_RADIUS` (int): Base player radius
- `START_VEL` (int): Initial movement velocity
- `keys_pressed` (set): Set of currently pressed keys

### Methods

#### `handle_events() -> bool`

Processes all pygame events.

**Returns:**

- `bool`: `False` if the game should quit, `True` otherwise

#### `handle_movement() -> None`

Processes player movement input and sends updates to the server.

## Input Mapping

### Movement

- `W`/`Up Arrow`: Move up
- `A`/`Left Arrow`: Move left
- `S`/`Down Arrow`: Move down
- `D`/`Right Arrow`: Move right

### Skills

- `Left Click`: Activate push skill
- `Right Click`: Activate pull skill

### Other Controls

- `ESC`: Quit game

## Features

- Smooth diagonal movement with normalization
- Configurable movement speed
- Server communication for movement and skill activation
- Clean separation of input handling from game logic

## Dependencies

- `pygame`: For input handling
- `typing`: For type hints
- `shared.utils.config_loader`: For game configuration
- `shared.packets`: For network communication
