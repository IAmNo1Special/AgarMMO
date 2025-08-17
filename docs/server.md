# `server.py` - Authoritative Game Server

The `server.py` script is the authoritative server for the game. It manages the game state, client connections, and all game logic.

## `ServerManager` Class

The `ServerManager` class is the core of the server.

### Initialization (`__init__`)

*   Initializes a `socket` for listening to client connections.
*   Loads server, network, world, player, and game configurations.
*   Initializes game state variables, including lists for players and food.
*   Creates a thread lock for thread-safe operations.

### Core Methods

*   **`connect_server()`**: Binds the server socket to the configured IP and port and starts listening for connections.
*   **`connection_thread()`**: Runs in a separate thread to accept new client connections. It creates a `ClientThread` for each new connection.
*   **`mainloop()`**: The main game loop of the server. It runs at a fixed tick rate and is responsible for:
    *   Updating skill statuses.
    *   Checking for collisions between players and food, and between players.
    *   Replenishing the food supply.
*   **`check_collision()`**: Handles collisions between players and food.
*   **`player_collision()`**: Handles collisions between players.
*   **`use_skill()`**: Applies the logic for player skills.
*   **`get_serializable_players()`**: Converts the list of `Player` objects into a dictionary that can be serialized to JSON.
*   **`shutdown()`**: Gracefully shuts down the server by closing all client connections and the main server socket.

## `ClientThread` Class

The `ClientThread` class handles communication with a single client.

### Core Methods

*   **`run()`**: The main method for the client thread. It receives the player's name, creates a `Player` object, and then enters a loop to receive and handle messages from the client.
*   **`_handle_message(message)`**: Parses messages from the client (e.g., "move", "push") and updates the game state accordingly.
*   **`_send_game_state()`**: Sends the current game state (as a JSON object) to the client.
*   **`cleanup()`**: Cleans up the connection when a client disconnects.

## Dependencies

*   `socket`, `threading`, `json`, `weakref`, `logging`: For networking, concurrency, data serialization, and logging.
*   `entities/player.py`, `entities/food.py`: To create and manage player and food objects.
*   `utils/config_loader.py`: For loading server and game configurations.
