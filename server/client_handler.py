import socket
import threading
import json
import time
import weakref
import logging
import select
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import asdict
from shared.config_loader import network_cfg, game_cfg, world_cfg, skills_cfg

from shared.entities.player import Player
from shared.entities.food import Food

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
            name_length_bytes = self.conn.recv(4)
            if not name_length_bytes or len(name_length_bytes) != 4:
                logger.error(f"[ERROR] Client {self.client_id}: Failed to receive name length")
                self.running = False
                return
            
            name_length = int.from_bytes(name_length_bytes, 'big')
            if name_length <= 0 or name_length > game_cfg['validation']['max_name_length']: # Max name length
                logger.error(f"[ERROR] Client {self.client_id}: Invalid name length: {name_length}")
                self.running = False
                return
            
            name_bytes = b''
            while len(name_bytes) < name_length:
                chunk = self.conn.recv(min(network_cfg['buffer_size'], name_length - len(name_bytes)))
                if not chunk:
                    break
                name_bytes += chunk
            
            name = name_bytes.decode('utf-8')

            with server.lock:
                if any(p.name == name for p in server.players.values()):
                    logger.warning(f"[ERROR] Client {self.client_id}: Username '{name}' is already taken.")
                    self.conn.sendall(network_cfg['protocol']['username_taken_message'].encode('utf-8'))
                    self.running = False
                    return

            logger.info(f"[LOG] Player '{name}' (ID: {self.client_id}) connected.")
            
            # Send player ID back to client
            response = f"{network_cfg['protocol']['player_id_prefix']}{self.client_id}".encode('utf-8')
            self.conn.sendall(len(response).to_bytes(4, 'big') + response)

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
                        
                    message = buffer[4:4+msg_length]
                    buffer = buffer[4+msg_length:]
                    self._handle_message(server, message.decode('utf-8'))

            except (socket.timeout, ConnectionResetError, ConnectionAbortedError):
                break
            except Exception as e:
                logger.error(f"Error handling client {self.client_id}: {e}", exc_info=True)
                break

    def _handle_message(self, server, message):
        if message.startswith("move "):
            parts = message.split()
            if len(parts) == 3:
                try:
                    dx, dy = float(parts[1]), float(parts[2])
                    with server.lock:
                        if self.client_id in server.players:
                            player = server.players[self.client_id]
                            player.move(dx, dy, *server.game_manager.world_dimensions, 
                                      world_cfg['boundary']['padding'])
                except (ValueError, IndexError) as e:
                    logger.warning(f"Invalid move command: {message}")
        elif message == "push":
            with server.lock:
                if self.client_id in server.players:
                    server.game_manager.use_skill(self.client_id, "push")
        elif message == "pull":
            with server.lock:
                if self.client_id in server.players:
                    server.game_manager.use_skill(self.client_id, "pull")
        elif message == "get":
            self._send_game_state(server)

    def _send_game_state(self, server):
        with server.lock:
            if self.client_id not in server.players:
                return
                
            game_state = {
                "balls": [b.to_dict() for b in server.balls],
                "players": server.game_manager.get_serializable_players(),
                "game_time": time.time() - server.start_time if server.start else 0
            }
            response = json.dumps(game_state).encode('utf-8')
            try:
                self.conn.sendall(len(response).to_bytes(4, 'big') + response)
            except (ConnectionResetError, BrokenPipeError):
                self.running = False

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