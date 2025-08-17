# `client/network.py` - Client-Side Networking

The `network.py` file provides the `Network` class, which handles all client-side communication with the game server.

## `Network` Class

### Initialization (`__init__`)

*   Loads the network configuration from `config/network.yaml`.
*   Initializes a socket for the connection.
*   Sets up thread locks for thread-safe operations.

### Core Methods

*   **`connect(name)`**: Connects to the server at the configured host and port. It sends the player's name and receives a player ID from the server.
*   **`disconnect()`**: Disconnects from the server and closes the socket.
*   **`send(data)`**: Sends data to the server. It prefixes the data with its length to ensure that full messages are received by the server.
*   **`get_game_state()`**: Sends a "get" request to the server and returns the received game state as a dictionary.
*   **`_send_with_retry()`**: A helper method that attempts to send data multiple times if the connection is lost, with exponential backoff.

## Dependencies

*   `socket`, `json`, `logging`: For networking, data serialization, and logging.
*   `shared/config_loader.py`: For loading network configuration.
