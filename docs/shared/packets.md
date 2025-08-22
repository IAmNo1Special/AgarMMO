# Network Packets

## Overview

This document describes the network packet structure used for client-server communication in AgarMMO. The packet system is designed to be lightweight, efficient, and extensible.

## Base Packet

### `Packet`

Base class for all network packets. Provides serialization and deserialization functionality.

```python
class Packet:
    """
    Base class for all network packets in AgarMMO.
    
    This class provides the foundation for all network communication between
    the client and server. All packet types must inherit from this class and
    define a unique 'type' class variable.
    """
    type: ClassVar[str]  # Must be overridden by subclasses
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the packet to a dictionary for serialization.
        
        Returns:
            Dictionary containing the packet data
        """
        pass
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Packet':
        """
        Create a packet from a dictionary.
        
        Args:
            data: Dictionary containing packet data
            
        Returns:
            A new Packet instance
        """
        pass
    
    def to_json(self) -> str:
        """
        Serialize the packet to a JSON string.
        
        Returns:
            JSON string representation of the packet
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Packet':
        """
        Deserialize a packet from a JSON string.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            A new Packet instance
        """
        return cls.from_dict(json.loads(json_str))
```

## Client-to-Server Packets

### `ConnectPacket`

Sent by client when initially connecting to the server.

**Type:** `"connect"`

**Attributes:**

- `name` (str): Player's chosen username (3-20 alphanumeric chars)
- `version` (str): Client version (e.g., "1.0.0")
- `client_id` (str, optional): Client-generated ID for reconnection

**Example:**

```json
{
  "type": "connect",
  "name": "Player1",
  "version": "1.0.0",
  "client_id": "abc123"
}
```

### `MovePacket`

Sent by client to update player movement.

**Type:** `"move"`

**Attributes:**

- `dx` (float): X-direction movement vector (normalized to [-1.0, 1.0])
- `dy` (float): Y-direction movement vector (normalized to [-1.0, 1.0])
- `sequence` (int): Client sequence number for packet ordering
- `timestamp` (float): Client timestamp for movement prediction

**Example:**

```json
{
  "type": "move",
  "dx": 0.7,
  "dy": -0.3,
  "sequence": 42,
  "timestamp": 12345.678
}
```

### `SkillPacket`

Sent by client to use a skill.

**Type:** `"skill"`

**Attributes:**

- `skill_name` (str): Name of the skill to activate
- `target_x` (float): X-coordinate of target position
- `target_y` (float): Y-coordinate of target position
- `direction` (float, optional): Direction in radians (for directional skills)

**Example:**

```json
{
  "type": "skill",
  "skill_name": "push",
  "target_x": 100.5,
  "target_y": 200.3,
  "direction": 1.57
}
```

### `GetGameStatePacket`

Requests the current game state from the server.

**Type:** `"get_game_state"`

**Attributes:**

- `full_update` (bool): If true, requests complete game state
- `last_ack` (int): Last processed server tick

**Example:**

```json
{
  "type": "get_game_state",
  "full_update": false,
  "last_ack": 1000
}
```

## Server-to-Client Packets

### `PlayerIdPacket`

Sent by server to assign a unique ID to a newly connected player.

**Type:** `"player_id"`

**Attributes:**

- `player_id` (str): Assigned player UUID
- `spawn_position` (Dict[str, float]): Initial spawn position `{"x": 0.0, "y": 0.0}`
- `server_tick_rate` (int): Server's tick rate (updates per second)

**Example:**

```json
{
  "type": "player_id",
  "player_id": "550e8400-e29b-41d4-a716-446655440000",
  "spawn_position": {"x": 100.0, "y": 150.0},
  "server_tick_rate": 30
}
```

### `GameStatePacket`

Contains game state updates sent from server to clients.

**Type:** `"game_state"`

**Attributes:**

- `players` (Dict[str, Any]): Dictionary of player states
  - `position` (Dict[str, float]): Current position `{"x": 0.0, "y": 0.0}`
  - `radius` (float): Current radius
  - `score` (int): Current score
  - `health` (float, optional): Current health (if applicable)
- `food` (List[Dict[str, Any]]): List of food objects
  - `id` (str): Food item ID
  - `position` (Dict[str, float]): Position `{"x": 0.0, "y": 0.0}`
  - `type` (str): Food type (e.g., "normal", "powerup")
  - `value` (int): Score value
- `server_tick` (int): Current server tick number
- `timestamp` (float): Server timestamp when packet was sent
- `player_updates` (List[Dict], optional): Delta updates for players

**Example:**

```json
{
  "type": "game_state",
  "players": {
    "player1": {
      "position": {"x": 100.5, "y": 200.3},
      "radius": 25.0,
      "score": 1250,
      "health": 0.85
    }
  },
  "food": [
    {
      "id": "food123",
      "position": {"x": 150.0, "y": 300.0},
      "type": "normal",
      "value": 10
    }
  ],
  "server_tick": 1000,
  "timestamp": 1234567.890
}
```

### `UsernameTakenPacket`

Sent when a player tries to use an already taken username.

**Type:** `"username_taken"`

**Attributes:**

- `message` (str): Error message
- `suggestions` (List[str]): List of available username suggestions

**Example:**

```json
{
  "type": "username_taken",
  "message": "Username 'Player1' is already taken",
  "suggestions": ["Player1_123", "Player1_456"]
}
```

### `ServerFullPacket`

Sent when the server has reached maximum capacity.

**Type:** `"server_full"`

**Attributes:**

- `message` (str): Error message
- `max_players` (int): Maximum number of allowed players
- `queue_position` (int, optional): Position in queue if queuing is enabled

**Example:**

```json
{
  "type": "server_full",
  "message": "Server is full",
  "max_players": 100,
  "queue_position": 5
}
```

### `PingPacket` / `PongPacket`

Used for latency measurement and keep-alive.

**Types:** `"ping"`, `"pong"`

**Attributes:**

- `timestamp` (float): Unix timestamp when packet was sent
- `sequence` (int): Sequence number for RTT calculation
- `server_time` (float, pong only): Current server time when pong was sent

**Example (Ping):**

```json
{
  "type": "ping",
  "timestamp": 1234567.890,
  "sequence": 42
}
```

**Example (Pong):**

```json
{
  "type": "pong",
  "timestamp": 1234567.890,
  "sequence": 42,
  "server_time": 1234568.100
}
```

## Conclusion

This documentation provides a comprehensive reference for the network protocol used in AgarMMO. The protocol is designed with the following goals in mind:

### Key Design Principles

1. **Simplicity**: Uses JSON for readability and ease of debugging
2. **Extensibility**: New packet types can be added without breaking existing clients
3. **Efficiency**: Delta compression and batching minimize bandwidth usage
4. **Reliability**: Sequence numbers and timestamps ensure correct packet ordering
5. **Security**: Input validation and rate limiting protect against common attacks

### Implementation Tips

- **Client-side**:
  - Implement interpolation for smooth movement between game state updates
  - Use client-side prediction for responsive controls
  - Handle packet loss and network latency gracefully

- **Server-side**:
  - Validate all incoming data
  - Implement rate limiting and anti-cheat measures
  - Optimize broadcast frequency based on network conditions

### Testing and Debugging

- Use the provided JSON examples for testing
- Log all sent and received packets during development
- Monitor network traffic for performance optimization
- Test with various network conditions (high latency, packet loss)

### Future Improvements

- Consider binary protocols (like MessagePack) for production
- Add compression for large game states
- Implement WebRTC for peer-to-peer communication
- Add support for voice chat and other real-time features

## Related Documents

- [Client Architecture](client/architecture.md)
- [Server Architecture](server/architecture.md)
- [Game State Management](shared/game_state.md)
- [Performance Optimization](performance.md)

## Network Protocol

### Message Format

All network messages follow this JSON structure:

```typescript
interface BasePacket {
  type: string;           // Packet type identifier
  [key: string]: any;     // Additional packet-specific fields
}
```

### Communication Flow

1. **Connection**
   - Client sends `ConnectPacket` with player name and version
   - Server responds with `PlayerIdPacket` containing player ID and initial game state

2. **Gameplay**
   - Client sends `MovePacket` for player movement
   - Client sends `SkillPacket` for skill usage
   - Server broadcasts `GameStatePacket` at regular intervals
   - Client can request full state with `GetGameStatePacket`

3. **Keep-alive**
   - Either side can send `PingPacket`
   - Recipient must respond with `PongPacket` containing original timestamp

### Error Handling

- Invalid packets should be logged and ignored
- Malformed JSON should close the connection
- Unexpected disconnections should be handled gracefully
- Clients should implement reconnection logic

### Performance Considerations

- Use delta compression for game state updates
- Batch small packets when possible
- Consider binary protocols (like MessagePack) for production
- Implement packet loss and latency compensation

### Security Considerations

- Validate all incoming data
- Sanitize player names and chat messages
- Rate limit client packets
- Consider encryption for sensitive data
- Implement anti-cheat measures

## Implementation Example

### Client Implementation

```python
class GameClient:
    def __init__(self, server_address):
        self.ws = websocket.WebSocket()
        self.ws.connect(server_address)
        self.player_id = None
        self.last_ping = time.time()
        
    def handle_packet(self, data):
        packet = Packet.from_json(data)
        if isinstance(packet, PlayerIdPacket):
            self.player_id = packet.player_id
        elif isinstance(packet, GameStatePacket):
            self.update_game_state(packet)
        elif isinstance(packet, PingPacket):
            self.send_packet(PongPacket(
                timestamp=packet.timestamp,
                sequence=packet.sequence
            ))
    
    def send_move(self, dx: float, dy: float):
        self.send_packet(MovePacket(
            dx=dx,
            dy=dy,
            sequence=self.sequence_number,
            timestamp=time.time()
        ))
        self.sequence_number += 1
```

### Server Implementation

```python
class GameServer:
    def __init__(self):
        self.clients = {}
        self.game_state = GameState()
        
    def handle_connection(self, websocket):
        try:
            async for message in websocket:
                packet = Packet.from_json(message)
                if isinstance(packet, ConnectPacket):
                    self.handle_connect(websocket, packet)
                elif isinstance(packet, MovePacket):
                    self.handle_move(websocket, packet)
                elif isinstance(packet, PingPacket):
                    self.send_packet(websocket, PongPacket(
                        timestamp=packet.timestamp,
                        sequence=packet.sequence,
                        server_time=time.time()
                    ))
        except websockets.exceptions.ConnectionClosed:
            self.handle_disconnect(websocket)
```
