# `client/network.py` - Client-Side Networking

The `network.py` file provides the `Network` class, which handles all client-side communication with the game server using a defined packet-based protocol.

## `Network` Class

### Initialization (`__init__`)

*   Loads the network configuration from `config/network.yaml`.
*   Initializes a socket for the connection.
*   Sets up thread locks for thread-safe operations.

### Core Methods

*   **`connect(name)`**: Connects to the server at the configured host and port. It sends a `ConnectPacket` containing the player's name and expects a `PlayerIdPacket` in return. It also handles `UsernameTakenPacket` and `ServerFullPacket` responses.
*   **`disconnect()`**: Disconnects from the server and closes the socket.
*   **`send(packet)`**: Sends a `Packet` object to the server. The packet is serialized to JSON and prefixed with its length to ensure full message delivery.
*   **`receive()`**: Receives and deserializes a `Packet` object from the server. Handles `PingPacket` and automatically sends `PongPacket` responses.
*   **`get_game_state()`**: Sends a `GetGameStatePacket` request to the server and returns the received `GameStatePacket` (converted to a dictionary for compatibility with existing game logic).
*   **`ping()`**: Sends a `PingPacket` to the server and expects a `PongPacket` response to check connection status.
*   **`_send_with_retry(packet)`**: A helper method that attempts to send a `Packet` multiple times if the connection is lost, with exponential backoff, and waits for a response `Packet`.

## Dependencies

*   `socket`, `json`, `logging`: For networking, data serialization, and logging.
*   `shared/config_loader.py`: For loading network configuration.
*   `shared/packets.py`: Defines the various packet types used for communication.
