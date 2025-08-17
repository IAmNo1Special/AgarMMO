# Server-Side Architecture

The server-side of the game is now modularized into several components to improve organization, maintainability, and separation of concerns.

## `server/main.py` - Server Entry Point

This is the main entry point for the server application. It is responsible for:
*   Initializing core game components like `GameManager` and `NetworkManager`.
*   Starting the server's main loop.

## `server/network_manager.py` - Network Management

This module contains the `NetworkManager` class, which handles all network-related operations on the server side. Its responsibilities include:
*   Binding the server socket and listening for incoming connections.
*   Managing client connections, including rate limiting and handling disconnections.
*   Creating and managing `ClientThread` instances for each connected client.
*   Orchestrating the main server loop, which includes processing game updates and maintaining the tick rate.

## `server/game_manager.py` - Game Logic Management

This module contains the `GameManager` class, which encapsulates all core game logic on the server side. Its responsibilities include:
*   Initializing game entities like food.
*   Handling collisions between players and food.
*   Handling collisions between players (eating mechanics).
*   Managing and applying player skills (e.g., "push" and "pull" skills), including logic for how skill effectiveness is influenced by the size of the affected object. For the push skill, if the target is too large, the player using the skill will be pushed away instead. For the pull skill, if the target is too large, the skill will have no effect.
*   Enforcing world boundaries for game objects.
*   Generating new food items to maintain supply.
*   Determining valid starting locations for new players.
*   Providing serializable representations of game entities for client updates.

## `server/client_handler.py` - Client Communication Handler

This module contains the `ClientThread` class, which is responsible for managing communication with a single connected client. Each client has its own `ClientThread`. Its responsibilities include:
*   Receiving player names during initial connection.
*   Handling incoming messages from the client (e.g., movement commands, skill usage requests).
*   Sending game state updates to its respective client.
*   Managing the client's connection lifecycle (e.g., timeouts, disconnections).

## Dependencies

*   `socket`, `threading`, `json`, `weakref`, `logging`, `select`: Core Python libraries for networking, concurrency, data serialization, and logging.
*   `shared/config_loader.py`: For loading server and game configurations.
*   `shared/entities/player.py`, `shared/entities/food.py`: To create and manage player and food objects.
*   `server/game_manager.py`: Used by `server/network_manager.py` and `server/client_handler.py` for game logic.
*   `server/network_manager.py`: The main server component.
*   `server/client_handler.py`: Used by `server/network_manager.py` to handle individual clients.

