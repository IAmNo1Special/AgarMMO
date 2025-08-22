# Network Manager Module

The `network_manager.py` module handles all network-related functionality for the game server, including client connections, message routing, and game state synchronization.

## Class: `NetworkManager`

Manages network connections and communication between the server and clients.

### Initialization

```python
def __init__(self, game_manager: GameManager, players: Dict[int, Player], 
             balls: List[Food], lock: threading.RLock):
    """
    Initialize the network manager with game components.
    
    Args:
        game_manager: Reference to the game manager instance
        players: Dictionary of connected players
        balls: List of food items in the game
        lock: Threading lock for thread safety
    """
```

### Attributes

- `game_manager` (GameManager): Reference to the game manager instance
- `players` (Dict[int, Player]): Dictionary of connected players
- `balls` (List[Food]): List of food items in the game
- `lock` (threading.RLock): Threading lock for thread safety
- `server_socket` (socket.socket): Main server socket
- `running` (bool): Flag indicating if the server is running
- `clients` (Dict[int, ClientThread]): Active client connections
- `config` (dict): Loaded configuration
- `logger` (logging.Logger): Logger instance

### Methods

#### `connect_server() -> bool`

Initializes and starts the server socket.

**Returns:**

- `bool`: True if server started successfully, False otherwise

#### `start() -> None`

Begins accepting client connections in a new thread.

#### `stop() -> None`

Stops the server and cleans up resources.

#### `broadcast(packet: Packet) -> None`

Sends a packet to all connected clients.

**Parameters:**

- `packet` (Packet): The packet to broadcast

#### `send_to_client(client_id: int, packet: Packet) -> bool`

Sends a packet to a specific client.

**Parameters:**

- `client_id` (int): ID of the target client
- `packet` (Packet): The packet to send

**Returns:**

- `bool`: True if sent successfully, False otherwise

#### `remove_client(client_id: int) -> None`

Removes a disconnected client.

**Parameters:**

- `client_id` (int): ID of the client to remove

## Connection Management

### Client Connections

- Handles new client connections
- Validates client authentication
- Tracks connection state
- Implements connection rate limiting

### Client Lifecycle

- Manages client disconnections
- Handles connection timeouts
- Cleans up resources on disconnect
- Notifies game manager of player departures

## Thread Management

### Thread Safety

- Uses `RLock` for thread-safe operations
- Implements proper locking for shared resources
- Handles concurrent access to client list

### Resource Management

- Proper cleanup of socket resources
- Thread pool management
- Memory leak prevention

## Game State Synchronization

### State Updates

- Broadcasts game state to all clients
- Implements efficient delta compression
- Handles client interpolation
- Manages update frequency

### Event Handling

- Processes player input
- Broadcasts game events
- Synchronizes game start/end
- Manages player join/leave events

## Configuration

Loaded from YAML configuration files:

- `network_cfg`: Network and connection settings
  - `host`: Server hostname/IP
  - `port`: Server port
  - `max_connections`: Maximum concurrent clients
  - `timeout`: Connection timeout in seconds

- `server_cfg`: Server-specific parameters
  - `tick_rate`: Game update frequency
  - `max_ping`: Maximum allowed ping
  - `rate_limit`: Connection rate limiting

- `game_cfg`: Game-related network settings
  - `player_update_rate`: How often to send player updates
  - `world_update_rate`: How often to send world state
  - `interpolation`: Client-side interpolation settings

## Dependencies

### Standard Library

- `socket`: For low-level network communication
- `threading`: For concurrent connection handling
- `logging`: For server event logging
- `weakref`: For managing object references
- `select`: For I/O multiplexing
- `time`: For timing operations

### Project Modules

- `shared.entities.player`: Player class definition
- `shared.entities.food`: Food class definition
- `server.client_handler`: Client thread implementation
- `server.game_manager`: Game logic implementation
- `shared.utils.config_loader`: Configuration management

## Error Handling

### Network Errors

- Handles socket errors gracefully
- Recovers from connection drops
- Implements exponential backoff for reconnections
- Logs network-related issues

### Protocol Errors

- Validates incoming packets
- Handles malformed data
- Enforces protocol versioning
- Logs protocol violations

## Performance Considerations

- Implements efficient packet batching
- Uses non-blocking I/O
- Minimizes lock contention
- Optimizes bandwidth usage
- Implements client-side prediction
