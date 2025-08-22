import socket
import json
import logging
import time
from typing import Any, Optional, Tuple, Dict, List, Union, Callable, TypeVar, Type, cast
from dataclasses import dataclass
from threading import Lock, RLock

from shared.utils.config_loader import network_cfg, game_cfg
from shared.packets import Packet, ConnectPacket, MovePacket, SkillPacket, GetGameStatePacket, \
    PlayerIdPacket, GameStatePacket, UsernameTakenPacket, ServerFullPacket, PingPacket, PongPacket

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class NetworkError(Exception):
    """Base class for network-related errors."""
    pass

class ConnectionError(NetworkError):
    """Raised when a connection error occurs."""
    pass

class TimeoutError(NetworkError):
    """Raised when a network operation times out."""
    pass

class ProtocolError(NetworkError):
    """Raised when a protocol error occurs."""
    pass

@dataclass
class ConnectionConfig:
    """Configuration for network connections."""
    host: str = network_cfg.get('host', 'localhost')
    port: int = network_cfg.get('port', 5555)
    timeout: float = network_cfg.get('timeout', 5.0)
    reconnect_attempts: int = network_cfg.get('reconnect_attempts', 3)
    reconnect_delay: float = network_cfg.get('reconnect_delay', 1.0)
    reconnect_backoff: float = network_cfg.get('reconnect_backoff', 1.5)
    max_message_size: int = network_cfg.get('max_message_size', 10 * 1024 * 1024)
    buffer_size: int = network_cfg.get('buffer_size', 4096)
    keepalive: bool = network_cfg['keepalive']['enabled']
    keepalive_interval: float = network_cfg['keepalive']['interval']
    keepalive_timeout: float = network_cfg['keepalive']['timeout']

class Network:
    """Thread-safe network client with reconnection and error handling."""
    
    def __init__(self, config: Optional[ConnectionConfig] = None):
        """Initialize the network client.
        
        Args:
            config: Optional configuration for the network connection.
                   If not provided, uses values from network_cfg.
        """
        self._config = config or self._load_network_config()
        self._socket: Optional[socket.socket] = None
        self._lock = RLock()
        self._connected = False
        self._player_id: Optional[str] = None
        self._last_activity = 0.0
        self._reconnect_attempts = 0
        self._should_reconnect = True
        self._shutdown_event = False
        self._message_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self._default_handler: Optional[Callable[[Dict[str, Any]], None]] = None
        
        # Initialize socket
        self._init_socket()
    
    def _load_network_config(self) -> ConnectionConfig:
        """Load configuration from network_cfg."""
        return ConnectionConfig(
            host=network_cfg.get('host', 'localhost'),
            port=network_cfg.get('port', 5555),
            timeout=network_cfg.get('timeout', 5.0),
            reconnect_attempts=network_cfg.get('reconnect_attempts', 3),
            reconnect_delay=network_cfg.get('reconnect_delay', 1.0),
            reconnect_backoff=network_cfg.get('reconnect_backoff', 1.5),
            max_message_size=network_cfg.get('max_message_size', 10 * 1024 * 1024),
            buffer_size=network_cfg.get('buffer_size', 4096),
            keepalive=network_cfg['keepalive']['enabled'],
            keepalive_interval=network_cfg['keepalive']['interval'],
            keepalive_timeout=network_cfg['keepalive']['timeout']
        )
        
    def _init_socket(self) -> None:
        """Initialize the socket with proper settings."""
        with self._lock:
            if self._socket:
                try:
                    self._socket.close()
                except:
                    pass
                    
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Platform-specific keepalive settings
            if hasattr(socket, 'TCP_KEEPIDLE') and hasattr(socket, 'TCP_KEEPINTVL') and hasattr(socket, 'TCP_KEEPCNT'):
                # Linux
                self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, network_cfg['keepalive']['tcp_keepidle'])
                self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, network_cfg['keepalive']['tcp_keepintvl'])
                self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, network_cfg['keepalive']['tcp_keepcnt'])
            elif hasattr(socket, 'SIO_KEEPALIVE_VALS'):
                # Windows
                self._socket.ioctl(
                    socket.SIO_KEEPALIVE_VALS,
                    (1,  # enable
                     int(self._config.keepalive_interval * 1000),  # time in ms
                     int(self._config.keepalive_timeout * 1000))   # interval in ms
                )

    

    def connect(self, name: str, timeout: Optional[float] = None) -> bool:
        """Connect to the server and send player name.
        
        Args:
            name: Player name to register with the server.
            timeout: Optional connection timeout in seconds.
            
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Player name must be a non-empty string")
            
        with self._lock:
            if self._connected:
                logger.warning("Already connected to server")
                return True
                
            self._should_reconnect = True
            self._reconnect_attempts = 0
            
            # Apply connection timeout if specified
            connect_timeout = timeout or self._config.timeout
            
            try:
                # Initialize socket if needed
                if not self._socket:
                    self._init_socket()
                    
                if not self._socket:
                    raise ConnectionError("Failed to initialize socket")
                    
                # Set socket timeout for connection attempt
                self._socket.settimeout(connect_timeout)
                
                # Connect to server
                logger.info(f"Connecting to {self._config.host}:{self._config.port}...")
                self._socket.connect((self._config.host, self._config.port))
                self._connected = True
                self._reconnect_attempts = 0
                self._last_activity = time.time()
                
                # Send connect packet
                connect_packet = ConnectPacket(name=name)
                self._send_message(connect_packet.to_json().encode('utf-8'))
                
                # Get response
                response_data = self._recv_message()
                if not response_data:
                    raise ConnectionError("No response from server")
                
                response_packet = Packet.from_json(response_data.decode('utf-8'))

                if isinstance(response_packet, PlayerIdPacket):
                    self._player_id = response_packet.player_id
                    logger.info(f"Connected with player ID: {self._player_id}")
                    return True
                elif isinstance(response_packet, UsernameTakenPacket):
                    raise ConnectionError(response_packet.message)
                elif isinstance(response_packet, ServerFullPacket):
                    raise ConnectionError(response_packet.message)
                else:
                    raise ProtocolError(f"Unexpected server response packet type: {response_packet.type}")
                    
            except socket.timeout as e:
                raise TimeoutError(f"Connection timeout after {connect_timeout} seconds") from e
            except (socket.error, OSError) as e:
                self._handle_connection_error(e)
                return False
                
    def _send_all(self, data: bytes) -> None:
        """Send all data through the socket with error handling."""
        if not self._socket:
            raise ConnectionError("Not connected to server")
            
        total_sent = 0
        while total_sent < len(data):
            try:
                sent = self._socket.send(data[total_sent:])
                if sent == 0:
                    raise ConnectionError("Socket connection broken")
                total_sent += sent
            except (socket.error, OSError) as e:
                self._handle_connection_error(e)
                raise ConnectionError("Failed to send data") from e
                
    def _recv_message(self) -> Optional[bytes]:
        """Receive a message with length prefix."""
        if not self._socket:
            raise ConnectionError("Not connected to server")
            
        try:
            # Get message length (first 4 bytes)
            length_bytes = self._recv_all(4)
            if not length_bytes:
                return None
                
            msg_length = int.from_bytes(length_bytes, 'big')
            if msg_length > self._config.max_message_size:
                raise ProtocolError(f"Message too large: {msg_length} bytes")
                
            # Get message data
            return self._recv_all(msg_length)
            
        except (socket.error, OSError) as e:
            self._handle_connection_error(e)
            raise ConnectionError("Failed to receive data") from e
            
    def _recv_all(self, length: int) -> Optional[bytes]:
        """Receive exactly 'length' bytes from the socket."""
        if not self._socket:
            return None
            
        chunks = []
        bytes_received = 0
        
        while bytes_received < length:
            try:
                chunk = self._socket.recv(min(length - bytes_received, self._config.buffer_size))
                if not chunk:
                    # Connection closed by peer
                    return None
                    
                chunks.append(chunk)
                bytes_received += len(chunk)
                
            except socket.timeout:
                raise TimeoutError("Receive operation timed out")
            except (socket.error, OSError) as e:
                self._handle_connection_error(e)
                raise ConnectionError("Receive failed") from e
                
        return b''.join(chunks) if chunks else None
        
    def _handle_connection_error(self, error: Exception) -> None:
        """Handle connection errors and attempt reconnection if needed."""
        with self._lock:
            self._connected = False
            
            if isinstance(error, (ConnectionRefusedError, ConnectionResetError)):
                logger.warning(f"Connection error: {error}")
            else:
                logger.error(f"Network error: {error}", exc_info=True)
                
            if self._should_reconnect and not self._shutdown_event:
                self._attempt_reconnect()
                
    def _attempt_reconnect(self) -> None:
        """Attempt to reconnect to the server with exponential backoff."""
        if self._reconnect_attempts >= self._config.reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            return
            
        self._reconnect_attempts += 1
        delay = self._config.reconnect_delay * (self._config.reconnect_backoff ** (self._reconnect_attempts - 1))
        
        logger.info(f"Attempting to reconnect (attempt {self._reconnect_attempts}/{self._config.reconnect_attempts}) in {delay:.1f}s...")
        
        try:
            time.sleep(delay)
            
            # Reinitialize socket
            self._init_socket()
            
            # Try to reconnect
            if self._socket and self._player_id:
                self._socket.connect((self._config.host, self._config.port))
                self._connected = True
                self._reconnect_attempts = 0
                
                # Notify server this is a reconnection
                reconnect_packet = PlayerIdPacket(player_id=self._player_id) # Reusing PlayerIdPacket for reconnect
                self.send(reconnect_packet)
                logger.info("Reconnection successful")
                
        except Exception as e:
            logger.warning(f"Reconnection attempt {self._reconnect_attempts} failed: {e}")
            if self._reconnect_attempts < self._config.reconnect_attempts:
                self._attempt_reconnect()

    def disconnect(self) -> None:
        """Disconnect from the server and clean up resources."""
        with self._lock:
            self._should_reconnect = False
            self._shutdown_event = True
            
            if self._socket:
                try:
                    # Send disconnect notification if connected
                    if self._connected and self._player_id:
                        try:
                            # No explicit disconnect packet, just close
                            pass
                        except:
                            pass  # Best effort
                    
                    # Shutdown and close socket
                    self._socket.shutdown(socket.SHUT_RDWR)
                    self._socket.close()
                except Exception as e:
                    logger.debug(f"Error during socket close: {e}")
                finally:
                    self._socket = None
                    self._connected = False
                    
            logger.info("Disconnected from server")

    def _send_message(self, data: bytes) -> None:
        """Send a message with length prefix."""
        if not self._socket or not self._connected:
            raise ConnectionError("Not connected to server")
            
        try:
            # Send message length (4 bytes, big-endian)
            length = len(data).to_bytes(4, 'big')
            self._send_all(length + data)
            self._last_activity = time.time()
        except (socket.error, OSError) as e:
            self._handle_connection_error(e)
            raise ConnectionError("Failed to send message") from e

    def send(self, packet: Packet) -> bool:
        """Send a Packet object to the server."""
        if not self._connected:
            logger.warning("Cannot send: not connected to server")
            return False
            
        with self._lock:
            try:
                message = packet.to_json().encode('utf-8')
                self._send_message(message)
                return True
            except (TypeError, json.JSONEncodeError) as e:
                logger.error(f"JSON encode error: {e}")
                return False
            except (socket.error, OSError, ConnectionError) as e:
                logger.error(f"Send error: {e}")
                return False
                
    def receive(self) -> Optional[Packet]:
        """Receive and parse a message from the server."""
        with self._lock:
            if not self._connected or not self._socket:
                raise ConnectionError("Not connected to server")
                
            # Receive message with length prefix
            data = self._recv_message()
            if data is None:
                self._handle_connection_error(ConnectionResetError("Connection closed by peer"))
                return None
                
            self._last_activity = time.time()
            
            # Try to parse as JSON and then as a Packet
            try:
                packet = Packet.from_json(data.decode('utf-8'))
                
                # Handle ping/pong at the network layer
                if isinstance(packet, PingPacket):
                    self.send(PongPacket())
                    return self.receive() # Get next message
                
                return packet
            except json.JSONDecodeError as e:
                raise ProtocolError(f"Invalid JSON received: {data}") from e
            except ValueError as e: # For unknown packet types from Packet.from_json
                raise ProtocolError(f"Protocol error: {e}") from e
                
    def is_connected(self) -> bool:
        """Check if the connection is active."""
        with self._lock:
            return self._connected and self._socket is not None
            
    def get_player_id(self) -> Optional[str]:
        """Get the current player ID."""
        with self._lock:
            return self._player_id
            
    def enable_reconnect(self, enable: bool = True) -> None:
        """Enable or disable automatic reconnection."""
        with self._lock:
            self._should_reconnect = enable
            
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        with self._lock:
            return {
                'connected': self._connected,
                'player_id': self._player_id,
                'reconnect_attempts': self._reconnect_attempts,
                'last_activity': self._last_activity,
                'should_reconnect': self._should_reconnect
            }
            
    def __del__(self) -> None:
        """Ensure proper cleanup when the object is garbage collected."""
        self.disconnect()

    def _send_with_retry(self, packet: Packet, max_retries: int = network_cfg['send_retries']) -> Optional[Packet]:
        """Send data with retry logic."""
        for attempt in range(max_retries + 1):
            try:
                if not self.is_connected():
                    if not self.reconnect():
                        continue
                        
                # Send the packet
                if not self.send(packet):
                    continue
                        
                # Receive response
                response_packet = self.receive()
                if response_packet is None:
                    print("[NETWORK] Failed to receive response packet")
                    continue
                        
                return response_packet
                        
            except (json.JSONDecodeError, UnicodeDecodeError, ProtocolError) as e:
                print(f"[NETWORK] Error processing response: {e}")
                if attempt >= max_retries:
                    break
                time.sleep(network_cfg['retry_sleep_duration'])
                        
            except socket.timeout:
                print("[NETWORK] Receive timed out")
                if attempt >= max_retries:
                    break
                        
            except Exception as e:
                print(f"[NETWORK] Error in send/receive (attempt {attempt + 1}/{max_retries + 1}): {e}")
                self._connected = False
                if attempt >= max_retries:
                    break
                time.sleep(network_cfg['retry_sleep_duration'])
                        
        print("[NETWORK] Max retries reached, giving up")
        return None

    def get_game_state(self) -> Optional[Dict[str, Any]]:
        """
        Request and return the current game state from the server.
        """
        response = self._send_with_retry(GetGameStatePacket())
        if isinstance(response, GameStatePacket):
            return response.to_dict() # Convert back to dict for existing game logic
        return None
        
    def ping(self) -> bool:
        """
        Send a ping to the server to check connection status.
        """
        try:
            response = self._send_with_retry(PingPacket())
            return isinstance(response, PongPacket)
        except Exception as e:
            print(f"[NETWORK] Ping failed: {e}")
            return False