# Network Module

The `network.py` module provides a robust, thread-safe network client for communicating with the game server, featuring automatic reconnection and error handling.

## Class: `NetworkError`

Base class for all network-related exceptions.

## Class: `ConnectionError`

Raised when a connection to the server cannot be established or is lost.

## Class: `TimeoutError`

Raised when a network operation exceeds the specified timeout.

## Class: `ProtocolError`

Raised when a protocol violation is detected in the communication with the server.

## Class: `ConnectionConfig`

Configuration for network connections.

### Attributes

- `host` (str): Server hostname or IP address
- `port` (int): Server port number
- `timeout` (float): Connection timeout in seconds
- `reconnect_attempts` (int): Maximum number of reconnection attempts
- `reconnect_delay` (float): Initial delay between reconnection attempts
- `reconnect_backoff` (float): Multiplier for delay between reconnection attempts
- `max_message_size` (int): Maximum allowed message size in bytes
- `buffer_size` (int): Socket buffer size
- `keepalive` (bool): Whether to enable TCP keepalive
- `keepalive_interval` (int): Interval between keepalive packets
- `keepalive_timeout` (int): Timeout for keepalive responses

## Class: `Network`

Thread-safe network client that handles communication with the game server.

### Initialization

```python
def __init__(self, config: Optional[ConnectionConfig] = None)
```

### Network Attributes

- `connected` (bool): Whether the client is connected to the server
- `player_id` (Optional[str]): Assigned player ID after connection
- `socket`: The underlying network socket
- `lock` (threading.Lock): Thread lock for thread safety
- `config` (ConnectionConfig): Network configuration

### Methods

#### `connect(name: str, timeout: Optional[float] = None) -> bool`

Establishes connection to the server.

**Parameters:**

- `name` (str): Player's display name
- `timeout` (Optional[float]): Connection timeout in seconds

**Returns:**

- `bool`: `True` on successful connection

#### `disconnect() -> None`

Gracefully disconnects from the server and cleans up resources.

#### `send(packet: Packet) -> bool`

Sends a packet to the server.

**Parameters:**

- `packet` (Packet): The packet to send

**Returns:**

- `bool`: `True` if successful

#### `receive() -> Optional[Packet]`

Receives a packet from the server.

**Returns:**

- `Optional[Packet]`: The received packet or `None` if no data is available

#### `get_game_state() -> Optional[Dict]`

Requests the current game state from the server.

**Returns:**

- `Optional[Dict]`: The game state dictionary or `None` on failure

## Features

- Automatic reconnection on connection loss
- Thread-safe operations
- Configurable timeouts and retries
- TCP keepalive support
- Message framing with length prefixes
- JSON-based protocol

## Error Handling

The network module implements comprehensive error handling including:

- Automatic reconnection on connection loss
- Timeout handling
- Protocol validation
- Resource cleanup

## Dependencies

- `socket`: For low-level network communication
- `json`: For message serialization
- `logging`: For error and debug logging
- `threading`: For thread safety
- `typing`: For type hints
- `shared.packets`: For packet definitions
- `shared.utils.config_loader`: For network configuration
