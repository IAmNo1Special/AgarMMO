import socket
import threading
import json
import time
import weakref
import logging
import select
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import asdict
from shared.utils.config_loader import network_cfg, game_cfg, world_cfg, skills_cfg

from shared.entities.player import Player
from shared.entities.food import Food
from shared.packets import Packet, ConnectPacket, MovePacket, SkillPacket, GetGameStatePacket, \
    PlayerIdPacket, GameStatePacket, UsernameTakenPacket, ServerFullPacket, PingPacket, PongPacket

logger = logging.getLogger(__name__)

class ClientThread(threading.Thread):
    def __init__(self, server_ref, conn, client_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_ref = server_ref
        self.conn = conn
        self.client_id = client_id
        self.running = True
        self.last_activity = time.time()

    def run(self):
        try:
            self._run()
        except Exception as e:
            logger.error(f"Client thread error: {e}", exc_info=True)
        finally:
            self.cleanup()

    def _run(self):
        server = self.server_ref()
        if not server:
            return

        # Initial name reception and player creation
        try:
            self.conn.settimeout(network_cfg['initial_name_timeout'])
            
            # Receive connect packet
            initial_data = self._recv_message()
            if not initial_data:
                logger.error(f"[ERROR] Client {self.client_id}: No initial data received.")
                self.running = False
                return

            initial_packet = Packet.from_json(initial_data.decode('utf-8'))

            if not isinstance(initial_packet, ConnectPacket):
                logger.error(f"[ERROR] Client {self.client_id}: Expected ConnectPacket, got {initial_packet.type}")
                self.running = False
                return

            name = initial_packet.name

            with server.lock:
                if any(p.name == name for p in server.players.values()):
                    logger.warning(f"[ERROR] Client {self.client_id}: Username '{name}' is already taken.")
                    self._send_message(UsernameTakenPacket(message=network_cfg['protocol']['username_taken_message']).to_json().encode('utf-8'))
                    self.running = False
                    return

            logger.info(f"[LOG] Player '{name}' (ID: {self.client_id}) connected.")
            
            # Send player ID back to client
            player_id_packet = PlayerIdPacket(player_id=str(self.client_id))
            self._send_message(player_id_packet.to_json().encode('utf-8'))

            x, y = server.game_manager.get_start_location(server.players)
            server.players[self.client_id] = Player(self.client_id, name, x, y)
            logger.info(f"[GAME] Created new player: {name} (ID: {self.client_id}) at ({x}, {y})")

        except socket.timeout:
            logger.error(f"[ERROR] Client {self.client_id}: Timeout receiving player name.")
            self.running = False
            return
        except Exception as e:
            logger.error(f"[ERROR] Client {self.client_id}: Error during initial connection: {e}", exc_info=True)
            self.running = False
            return

        # Continue with message handling loop
        buffer = b''
        while self.running and server.running:
            try:
                ready = select.select([self.conn], [], [], 1.0)
                if not ready[0]:
                    # Check for timeout
                    if time.time() - self.last_activity > network_cfg['client_timeout']:
                        logger.warning(f"Client {self.client_id} timed out")
                        break
                    continue

                data = self.conn.recv(network_cfg['buffer_size'])
                if not data:
                    break

                self.last_activity = time.time()
                buffer += data
                
                while len(buffer) >= 4 and self.running:
                    msg_length = int.from_bytes(buffer[:4], 'big')
                    if len(buffer) < 4 + msg_length:
                        break
                        
                    message_bytes = buffer[4:4+msg_length]
                    buffer = buffer[4+msg_length:]
                    
                    try:
                        packet = Packet.from_json(message_bytes.decode('utf-8'))
                        self._handle_packet(server, packet)
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.error(f"Client {self.client_id}: Invalid packet received: {e}")
                        # Optionally send an error packet back to the client
                        
            except (socket.timeout, ConnectionResetError, ConnectionAbortedError):
                break
            except Exception as e:
                logger.error(f"Error handling client {self.client_id}: {e}", exc_info=True)
                break

    def _handle_packet(self, server, packet: Packet):
        if isinstance(packet, MovePacket):
            with server.lock:
                if self.client_id in server.players:
                    player = server.players[self.client_id]
                    player.move(packet.dx, packet.dy, *server.game_manager.world_dimensions, 
                              world_cfg['boundary']['padding'])
        elif isinstance(packet, SkillPacket):
            with server.lock:
                if self.client_id in server.players:
                    server.game_manager.use_skill(self.client_id, packet.skill_name)
        elif isinstance(packet, GetGameStatePacket):
            self._send_game_state(server)
        elif isinstance(packet, PingPacket):
            self._send_message(PongPacket().to_json().encode('utf-8'))
        elif isinstance(packet, PlayerIdPacket): # Reconnect packet
            logger.info(f"Client {self.client_id} reconnected with ID: {packet.player_id}")
        else:
            logger.warning(f"Client {self.client_id}: Unhandled packet type: {packet.type}")

    def _send_game_state(self, server):
        with server.lock:
            if self.client_id not in server.players:
                return
                
            game_state = GameStatePacket(
                balls=[b.to_dict() for b in server.balls],
                players=server.game_manager.get_serializable_players(),
                game_time=time.time() - server.start_time if server.start else 0
            )
            response = game_state.to_json().encode('utf-8')
            try:
                self._send_message(response)
            except (ConnectionResetError, BrokenPipeError):
                self.running = False

    def _send_message(self, data: bytes) -> None: 
        """Send a message with length prefix."""
        if not self.conn:
            raise ConnectionResetError("Connection is closed")
        
        try:
            length = len(data).to_bytes(4, 'big')
            self.conn.sendall(length + data)
        except (socket.error, OSError) as e:
            logger.error(f"Error sending message to client {self.client_id}: {e}")
            raise

    def _recv_message(self) -> Optional[bytes]:
        """Receive a message with length prefix."""
        if not self.conn:
            return None
        
        try:
            length_bytes = self.conn.recv(4)
            if not length_bytes:
                return None
            
            msg_length = int.from_bytes(length_bytes, 'big')
            
            chunks = []
            bytes_received = 0
            while bytes_received < msg_length:
                chunk = self.conn.recv(min(network_cfg['buffer_size'], msg_length - bytes_received))
                if not chunk:
                    return None
                chunks.append(chunk)
                bytes_received += len(chunk)
            
            return b''.join(chunks)
        except (socket.error, OSError) as e:
            logger.error(f"Error receiving message from client {self.client_id}: {e}")
            return None

    def stop(self):
        self.running = False
        try:
            self.conn.close()
        except:
            pass

    def cleanup(self):
        self.stop()
        server = self.server_ref()
        if server:
            with server.lock:
                if self.client_id in server.players:
                    player_name = server.players[self.client_id].name
                    del server.players[self.client_id]
                    server.connections -= 1
                    logger.info(f"Player {player_name} (ID: {self.client_id}) disconnected")
