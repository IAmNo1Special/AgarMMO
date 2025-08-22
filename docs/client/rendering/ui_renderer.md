# UI Renderer

The `ui_renderer.py` module handles all user interface rendering for the game, including the scoreboard, player stats, and game information.

## Class: `UIRenderer`

Manages the rendering of all UI elements in the game, including the scoreboard, player statistics, and game information.

### Initialization

```python
def __init__(self, WIN: pygame.Surface, players: Dict[str, Any], game_time: int, 
             W: int, H: int, TIME_FONT: pygame.font.Font, SCORE_FONT: pygame.font.Font)
```

### Attributes

- `WIN` (pygame.Surface): The main game window surface
- `players` (Dict[str, Any]): Dictionary of all players
- `game_time` (int): Current game time in seconds
- `W` (int): Screen width
- `H` (int): Screen height
- `TIME_FONT` (pygame.font.Font): Font for time display
- `SCORE_FONT` (pygame.font.Font): Font for score display
- `ui_elements` (Dict[str, Any]): Dictionary of UI element positions and properties

### Methods

#### `draw_ui(player_score: int, player_age: int, growth_percentage: float) -> None`

Renders the complete UI.

**Parameters:**

- `player_score` (int): The current player's score
- `player_age` (int): The current player's age in seconds
- `growth_percentage` (float): The player's growth progress (0-100%)

#### `convert_time(t: Union[int, str]) -> str`

Static method to convert seconds to MM:SS format.

**Parameters:**

- `t` (Union[int, str]): Time in seconds or string to convert

**Returns:**

- `str`: Formatted time string (e.g., "1:30" or "45s")

## UI Elements

### Scoreboard

Displays top 3 players by score with their names and scores.

### Player Stats

Shows:

- World age
- Player age
- Growth percentage

### Growth Bar

Visual indicator of player's growth progress with color coding:

- Red (0-33%): Low growth
- Yellow (34-66%): Medium growth
- Green (67-100%): High growth

### Score Display

Shows current player's score at the bottom of the screen.

## Visual Features

- Semi-transparent backgrounds for better text readability
- Color-coded growth bar (red to green gradient)
- Clean, modern typography with configurable fonts
- Responsive layout that adapts to screen size
- Consistent padding and spacing
- Clear visual hierarchy

## Dependencies

- `pygame`: For all rendering operations
- `typing`: For type hints
- `shared.utils.config_loader`: For UI configuration
