"""
Refactored server script for running agar.io server with improved architecture
"""
import socket
import threading
import json
import time
import random
import math
import weakref
import logging
import select
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import asdict
from utils.config_loader import server_cfg, network_cfg, world_cfg, player_cfg, game_cfg, food_cfg, skills_cfg

from entities.player import Player
from entities.food import Food

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
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

            x, y = server.get_start_location(server.players)
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
                            player.move(dx, dy, *server.world_dimensions, 
                                      world_cfg['boundary']['padding'])
                except (ValueError, IndexError) as e:
                    logger.warning(f"Invalid move command: {message}")
        elif message == "push":
            with server.lock:
                if self.client_id in server.players:
                    server.use_skill(self.client_id, "push")
        elif message == "get":
            self._send_game_state(server)

    def _send_game_state(self, server):
        with server.lock:
            if self.client_id not in server.players:
                return
                
            game_state = {
                "balls": [b.to_dict() for b in server.balls],
                "players": server.get_serializable_players(),
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


class ServerManager:
    def __init__(self) -> None:
        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Use bind address from config, fallback to localhost
        self.server_ip = network_cfg['host']
        self.port = network_cfg['port']
        self.max_connections = network_cfg.get('max_connections', 10)
        self.running = False
        
        self.player_start_radius = player_cfg['start_radius']
        self.world_dimensions = (world_cfg['world_width'], world_cfg['world_height'])
        
        self.players: Dict[int, Player] = {}
        self.balls: List[Food] = []
        self.client_threads: Dict[int, ClientThread] = {}
        self.connections = 0
        self._id = 0
        
        self.player_colors = [tuple(color) for color in player_cfg['colors']]
        self.is_started = False
        self.start = False
        self.start_time = 0
        
        self.lock = threading.RLock()  # Use RLock for nested locking
        self.connection_attempts = {}
        
        self._initialize_food()

    def _initialize_food(self) -> None:
        """Initialize food items in the game world."""
        world_w, world_h = self.world_dimensions
        padding = world_cfg['boundary']['padding']
        
        for _ in range(server_cfg['ball_count']['min'], server_cfg['ball_count']['max']):
            x = random.randint(padding, world_w - padding)
            y = random.randint(padding, world_h - padding)
            color = random.choice(self.player_colors)
            self.balls.append(Food(x, y, color))

    def connect_server(self):
        """Initialize and start the server socket."""
        try:
            self.SOCKET.bind((self.server_ip, self.port))
            self.SOCKET.settimeout(1.0)  # Add timeout for accept()
            self.SOCKET.listen(self.max_connections)
            self.running = True
            
            # Log all available IP addresses
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            logger.info(f"Hostname: {hostname}")
            logger.info(f"Local IP: {local_ip}")
            logger.info(f"Server bound to: {self.server_ip}:{self.port}")
            logger.info(f"Maximum connections: {self.max_connections}")
            logger.info(f"World size: {self.world_dimensions[0]}x{self.world_dimensions[1]}")
            
            # Additional network info for debugging
            try:
                import netifaces
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            logger.info(f"Interface {interface} - IP: {addr['addr']} Netmask: {addr['netmask']}")
            except ImportError:
                logger.info("netifaces module not available, skipping interface details")
                
            self.is_started = True
            return True
            
        except socket.error as e:
            logger.error(f"Could not start server: {e}")
            logger.error(f"Tried to bind to {self.server_ip}:{self.port}")
            logger.error(f"Available IPs: {socket.gethostbyname_ex(socket.gethostname())[2]}")
            return False

    def check_collision(self, players, balls):
        """Check if any player has collided with any of the balls."""
        balls_to_remove = set()
        
        for player in players.values():
            for i, ball in enumerate(balls):
                if i in balls_to_remove:
                    continue
                    
                if player.is_colliding(ball):
                    player.grow(food_cfg['growth_amount'])
                    balls_to_remove.add(i)
        
        # Remove collided balls in reverse order to avoid index shifting
        for i in sorted(balls_to_remove, reverse=True):
            if i < len(balls):
                del balls[i]

    def player_collision(self, players):
        """Check for player collisions and handle them."""
        sorted_players = sorted(list(players.values()), key=lambda p: p.score)
        
        for i, player1 in enumerate(sorted_players):
            for player2 in sorted_players[i+1:]:
                if player1.is_colliding(player2):
                    if player2.score > player1.score * game_cfg['player_eating_threshold']:
                        player2.grow(player1.score)
                        player1.score = 0
                        player1.x, player1.y = self.get_start_location(players)
                        print(f"[GAME] {player2.name} ATE {player1.name}")
                    elif player1.score > player2.score * game_cfg['player_eating_threshold']:
                        player1.grow(player2.score)
                        player2.score = 0
                        player2.x, player2.y = self.get_start_location(players)
                        print(f"[GAME] {player1.name} ATE {player2.name}")

    def use_skill(self, player_id, skill_name):
        """Handle player skill usage."""
        print(f"[SKILL] Player {player_id} used {skill_name}")
        if skill_name == "push":
            pusher = self.players.get(player_id)
            if pusher:
                pusher.push_skill_active = True
                pusher.push_skill_end_time = time.time() + skills_cfg['push_skill']['duration']

    def update_skills(self):
        """Update active skills with optimized collision detection"""
        current_time = time.time()
        
        with self.lock:
            for player_id, player in list(self.players.items()):
                if not hasattr(player, 'push_skill_active') or not player.push_skill_active:
                    continue
                    
                if current_time > player.push_skill_end_time:
                    player.push_skill_active = False
                    continue
                    
                # Get push skill parameters
                push_skill = player.skills.get('push')
                if not push_skill:
                    continue
                    
                # Get push radius from skill
                push_radius = getattr(push_skill, 'radius', skills_cfg['push_skill']['base_radius'])
                
                # Calculate push force based on skill level
                push_force = getattr(push_skill, 'push_force', skills_cfg['push_skill']['push_force'])
                
                # Check collisions with other players
                for other_id, other_player in list(self.players.items()):
                    if player_id == other_id:
                        continue
                        
                    if self._is_in_push_range(player, other_player, push_radius):
                        # Calculate push direction and apply force
                        dx = other_player.x - player.x
                        dy = other_player.y - player.y
                        distance = max(1, math.sqrt(dx*dx + dy*dy))
                        
                        # Normalize and scale by push force
                        scale = push_force * (1 - (distance / push_radius))
                        other_player.x += dx * scale / distance
                        other_player.y += dy * scale / distance
                        self._enforce_world_boundaries(other_player)
                
                # Check collisions with balls
                for ball in self.balls:
                    if self._is_in_push_range(player, ball, push_radius):
                        dx = ball.x - player.x
                        dy = ball.y - player.y
                        distance = max(1, math.sqrt(dx*dx + dy*dy))
                        
                        # Normalize and scale by push force
                        scale = push_force * (1 - (distance / push_radius))
                        ball.x += dx * scale / distance
                        ball.y += dy * scale / distance
                        self._enforce_world_boundaries(ball)
    
    def _is_in_push_range(self, obj1, obj2, push_radius):
        """Check if two objects are within push range of each other"""
        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance_sq = dx*dx + dy*dy
        max_distance = (obj1.radius + obj2.radius + push_radius) ** 2
        return distance_sq <= max_distance

    def _enforce_world_boundaries(self, game_object):
        """Ensure a game object stays within the world boundaries"""
        padding = world_cfg['boundary']['padding']
        world_w, world_h = self.world_dimensions
        radius = game_object.radius + (game_object.score if hasattr(game_object, 'score') else 0)
        game_object.x = max(padding + radius, min(game_object.x, world_w - padding - radius))
        game_object.y = max(padding + radius, min(game_object.y, world_h - padding - radius))

    def create_balls(self, n):
        """creates orbs/balls in the game world"""
        world_w, world_h = self.world_dimensions
        padding = world_cfg['boundary']['padding']
        for _ in range(n):
            x = random.randint(padding, world_w - padding)
            y = random.randint(padding, world_h - padding)
            self.balls.append(Food(x, y, random.choice(self.player_colors)))

    def get_start_location(self, players):
        """picks a start location for a player"""
        world_w, world_h = self.world_dimensions
        padding = world_cfg['boundary']['padding']
        
        for _ in range(world_cfg['start_location_attempts']):
            x = random.randint(padding, world_w - padding)
            y = random.randint(padding, world_h - padding)
            valid_position = True
            for player in players.values():
                dis = math.sqrt((x - player.x)**2 + (y - player.y)**2)
                if dis <= self.player_start_radius + player.score + padding:
                    valid_position = False
                    break
            if valid_position:
                return (x, y)
        return (random.randint(padding, world_w - padding), random.randint(padding, world_h - padding))

    def get_serializable_players(self):
        """Convert Player objects to a serializable dictionary"""
        return {pid: p.to_dict() for pid, p in self.players.items()}

    

    def mainloop(self):
        """Main game loop with proper cleanup."""
        logger.info("Setting up level")
        logger.info("Waiting for connections")

        try:
            # Start connection thread
            conn_thread = threading.Thread(target=self.connection_thread, daemon=True)
            conn_thread.start()
            
            last_time = time.time()
            tick_rate = 1.0 / game_cfg['tick_rate']
            
            while self.running:
                try:
                    current_time = time.time()
                    delta_time = current_time - last_time
                    last_time = current_time
                    
                    # Process game updates
                    if self.start:
                        with self.lock:
                            self.update_skills()
                            self.check_collision(self.players, self.balls)
                            self.player_collision(self.players)
                            
                            # Maintain ball count
                            min_balls = server_cfg['ball_count']['min']
                            max_balls = server_cfg['ball_count']['max']
                            if len(self.balls) < min_balls:
                                to_add = min(max_balls - len(self.balls), max_balls - min_balls + 1)
                                if to_add > 0:
                                    self.create_balls(to_add)
                    
                    # Calculate sleep time to maintain consistent tick rate
                    elapsed = time.time() - current_time
                    sleep_time = max(0, tick_rate - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        
                except KeyboardInterrupt:
                    logger.info("Shutting down server...")
                    self.shutdown()
                    break
                except Exception as e:
                    logger.error(f"Error in game loop: {e}", exc_info=True)
                    time.sleep(game_cfg['error_sleep_duration'])  # Prevent tight error loop
                    
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean up resources and shut down the server."""
        if not self.running:
            return
            
        self.running = False
        
        # Close all client connections
        for thread in list(self.client_threads.values()):
            thread.stop()
        
        # Clear client threads
        self.client_threads.clear()
        
        # Close server socket
        try:
            self.SOCKET.close()
        except:
            pass
            
        logger.info("Server shutdown complete")

    def connection_thread(self):
        """Handle new client connections with rate limiting."""
        while self.running:
            try:
                try:
                    conn, addr = self.SOCKET.accept()
                except socket.timeout:
                    continue
                except OSError as e:
                    if not self.running:
                        break
                    raise
                
                client_ip = addr[0]
                current_time = time.time()
                
                # Rate limiting
                with self.lock:
                    # Clean up old connection attempts
                    for ip, timestamps in list(self.connection_attempts.items()):
                        valid_timestamps = [ts for ts in timestamps if current_time - ts < 60]
                        if valid_timestamps:
                            self.connection_attempts[ip] = valid_timestamps
                        else:
                            del self.connection_attempts[ip]
                    
                    # Check connection rate limit (e.g., 5 connections per minute per IP)
                    if len(self.connection_attempts.get(client_ip, [])) >= 5:
                        logger.warning(f"Connection rate limit exceeded for {client_ip}")
                        conn.close()
                        continue
                    
                    # Record connection attempt
                    if client_ip not in self.connection_attempts:
                        self.connection_attempts[client_ip] = []
                    self.connection_attempts[client_ip].append(current_time)
                    
                    # Check max connections
                    if self.connections >= self.max_connections:
                        logger.warning(f"Max connections ({self.max_connections}) reached")
                        conn.sendall(b"SERVER_FULL")
                        conn.close()
                        continue
                    
                    if not self.start:
                        self.start = True
                        self.start_time = current_time
                        logger.info("Game Started")
                    
                    # Create client thread
                    current_id = self._id
                    self._id += 1
                    self.connections += 1
                    
                    # Create and start client thread
                    client_thread = ClientThread(
                        weakref.ref(self),
                        conn,
                        current_id
                    )
                    client_thread.daemon = True
                    self.client_threads[current_id] = client_thread
                    client_thread.start()
                    
                    logger.info(f"New connection from {addr} (ID: {current_id})")
                    
            except Exception as e:
                if self.running:  # Only log if we're not shutting down
                    logger.error(f"Error in connection thread: {e}", exc_info=True)
                break

if __name__ == "__main__":
    server = ServerManager()
    if server.connect_server():
        server.mainloop()
