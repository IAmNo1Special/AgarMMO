# Game Renderer

The `game_renderer.py` module handles all game rendering functionality using Pygame.

## Class: `GameRenderer`

Handles the rendering of all game elements including players, food balls, and skill effects.

### Initialization

```python
def __init__(self, WIN: pygame.Surface, players: Dict[str, Any], balls: List[Any], 
             camera_x: int, camera_y: int, W: int, H: int, WORLD_W: int, WORLD_H: int, 
             PLAYER_RADIUS: int, BALL_RADIUS: int, NAME_FONT: pygame.font.Font, 
             PLAYER_COLORS: List[Tuple[int, int, int]], 
             FOOD_COLORS: List[Tuple[int, int, int]])
```

### Attributes

- `WIN` (pygame.Surface): The main game window surface
- `players` (Dict[str, Any]): Dictionary of all players
- `balls` (List[Any]): List of all food balls
- `camera_x` (int): Current camera x-coordinate
- `camera_y` (int): Current camera y-coordinate
- `W` (int): Screen width
- `H` (int): Screen height
- `WORLD_W` (int): World width
- `WORLD_H` (int): World height
- `PLAYER_RADIUS` (int): Base player radius
- `BALL_RADIUS` (int): Food ball radius
- `NAME_FONT` (pygame.font.Font): Font for rendering player names
- `PLAYER_COLORS` (List[Tuple[int, int, int]]): Available player colors
- `FOOD_COLORS` (List[Tuple[int, int, int]]): Available food colors

### Methods

#### `draw() -> None`

Main drawing method that renders the complete game state.

#### `draw_boundary() -> None`

Renders the game world boundary.

#### `draw_balls() -> None`

Renders all food balls within the visible area.

#### `draw_players() -> None`

Renders all players with their current state including:

- Player circles with dynamic radius
- Push skill visualization when active
- Pull skill visualization when active
- Player names above their circles

## Rendering Features

- Efficiently renders only visible elements
- Handles camera-relative positioning
- Supports dynamic player sizes and colors
- Visual feedback for active skills (push/pull)
- Text rendering for player names
- Optimized for performance with large numbers of objects

## Dependencies

- `pygame`: For all rendering operations
- `typing`: For type hints
- `shared.utils.config_loader`: For game configuration
