# Client Handler Module

The `client_handler.py` module manages individual client connections to the game server, handling communication and player state synchronization.

## Class: `ClientThread`

A thread class that handles communication with a single connected client.

### Initialization

```python
def __init__(self, server_ref, conn, client_id, *args, **kwargs):
    """
    Initialize a new client thread.
    
    Args:
        server_ref: Weak reference to the game server instance
        conn: Client socket connection
        client_id: Unique identifier for this client
    """
```

### Attributes

- `server_ref` (weakref): Weak reference to the game server instance
- `conn` (socket.socket): Client socket connection
- `client_id` (int): Unique identifier for this client
- `player_name` (str): Name of the connected player
- `player` (Player): Reference to the player entity
- `running` (bool): Flag indicating if the thread should continue running
- `last_ping` (float): Timestamp of the last received ping
- `packet_handlers` (Dict[Type[Packet], Callable]): Maps packet types to handler methods
- `logger` (logging.Logger): Logger instance for this client
- `config` (dict): Loaded configuration

### Methods

#### `run() -> None`

Main thread entry point that handles the client connection lifecycle.

#### `_run() -> None`

Internal method containing the main client handling logic.

#### `handle_packet(packet: Packet) -> None`

Processes incoming packets from the client.

**Parameters:**

- `packet` (Packet): The received packet to process

#### `send_packet(packet: Packet) -> bool`

Sends a packet to the connected client.

**Parameters:**

- `packet` (Packet): The packet to send

**Returns:**

- `bool`: True if the packet was sent successfully, False otherwise

#### `cleanup() -> None`

Cleans up resources when the client disconnects.

### Packet Handling

The client thread handles the following packet types:

- `ConnectPacket`: Initial connection and player registration
- `MovePacket`: Player movement updates
- `SkillPacket`: Player skill activations
- `GetGameStatePacket`: Requests for current game state
- `PingPacket`: Connection keep-alive

### Packet Processing Flow

1. Receive raw data from socket
2. Deserialize into packet object
3. Look up handler for packet type
4. Execute handler with packet data
5. Send response if required

### Error Handling

#### Network Errors

- Handles socket timeouts
- Manages connection resets
- Logs network-related issues

#### Protocol Errors

- Validates packet structure
- Handles malformed packets
- Enforces protocol versioning

### Lifecycle

1. **Connection**

   - Client establishes TCP connection
   - Server creates new `ClientThread`
   - Performs initial handshake

2. **Authentication**

   - Validates player credentials
   - Registers player with game world
   - Sends initial game state

3. **Gameplay**

   - Processes incoming packets
   - Updates player state
   - Broadcasts game state updates

4. **Disconnection**

   - Graceful shutdown
   - Resource cleanup
   - Player removal from game world

### Thread Safety

#### Synchronization

- Uses `RLock` for thread-safe operations
- Implements proper locking for shared resources
- Handles concurrent access to game state

#### Resource Management

- Proper cleanup of socket resources
- Memory leak prevention
- Connection pooling

### Dependencies

#### Standard Library

- `socket`: For network communication
- `threading`: For concurrent client handling
- `logging`: For error and debug logging
- `weakref`: For managing server references
- `time`: For timing operations

#### Project Modules

- `shared.packets`: For packet definitions
- `shared.utils.config_loader`: For configuration
- `shared.entities.player`: Player class definition

## Performance Considerations

- Implements efficient packet batching
- Uses non-blocking I/O where appropriate
- Minimizes lock contention
- Optimizes memory usage for high player counts
