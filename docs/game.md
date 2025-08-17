# `client/game.py` - Client-Side Game Logic

The `game.py` file contains the `Game` class, which manages the client-side game logic, rendering, and user interaction.

## `Game` Class

### Initialization (`__init__`)

* Initializes `pygame`.
* Loads all necessary configurations from YAML files using `shared.config_loader`.
* Initializes game state variables (players, balls, camera, etc.).
* Initializes the game window.
* Initializes `GameRenderer` for drawing game objects.
* Initializes `UIRenderer` for drawing UI elements.
* Initializes `InputHandler` for handling user input.

### Core Methods

* **`load_config()`**: Loads and sets up game parameters from the configuration files.
* **`init_window()`**: Creates the game window with the dimensions and title specified in the configuration.
* **`connect_to_server(name)`**: Creates a `Network` object and connects to the server, sending the player's name.
* **`get_game_state()`**: Requests and receives the latest game state from the server.
* **`handle_events()`**: (Now handled by `InputHandler`) Manages `pygame` events, such as closing the window or mouse clicks for skills.
* **`handle_movement()`**: (Now handled by `InputHandler`) Detects keyboard input for player movement and sends movement commands to the server.
* **`draw()`**: The main rendering method. It delegates drawing of game objects to `GameRenderer` and UI elements to `UIRenderer`. It also updates the camera position to follow the player.
* **`run(player_name)`**: The main game loop. It connects to the server, and then continuously handles events (via `InputHandler`), gets the game state, handles movement (via `InputHandler`), and draws the screen, all while maintaining a consistent frame rate.
* **`cleanup()`**: Disconnects from the server and quits `pygame`.

## Dependencies

* `pygame`: For all rendering, input handling, and window management.
* `client/network.py`: To communicate with the server.
* `shared/config_loader.py`: For loading game settings.
* `client/rendering/game_renderer.py`: For drawing game objects.
* `client/rendering/ui_renderer.py`: For drawing UI elements.
* `client/input_handler.py`: For handling user input.
