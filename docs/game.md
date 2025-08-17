# `game.py` - Client-Side Game Logic

The `game.py` file contains the `Game` class, which manages the client-side game logic, rendering, and user interaction.

## `Game` Class

### Initialization (`__init__`)

*   Initializes `pygame`.
*   Loads all necessary configurations from YAML files using `utils.config_loader`.
*   Initializes game state variables (players, balls, camera, etc.).
*   Initializes the game window.

### Core Methods

*   **`load_config()`**: Loads and sets up game parameters from the configuration files.
*   **`init_window()`**: Creates the game window with the dimensions and title specified in the configuration.
*   **`connect_to_server(name)`**: Creates a `Network` object and connects to the server, sending the player's name.
*   **`get_game_state()`**: Requests and receives the latest game state from the server.
*   **`handle_events()`**: Manages `pygame` events, such as closing the window or mouse clicks for skills.
*   **`handle_movement()`**: Detects keyboard input for player movement and sends movement commands to the server.
*   **`draw()`**: The main rendering method. It clears the screen, draws the game boundary, food, players, and the UI. It also updates the camera position to follow the player.
*   **`run(player_name)`**: The main game loop. It connects to the server, and then continuously handles events, gets the game state, handles movement, and draws the screen, all while maintaining a consistent frame rate.
*   **`cleanup()`**: Disconnects from the server and quits `pygame`.

## Dependencies

*   `pygame`: For all rendering, input handling, and window management.
*   `network.py`: To communicate with the server.
*   `utils.config_loader.py`: For loading game settings.
