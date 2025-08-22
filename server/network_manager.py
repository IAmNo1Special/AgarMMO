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
from shared.utils.config_loader import server_cfg, network_cfg, world_cfg, player_cfg, game_cfg, food_cfg, skills_cfg

from shared.entities.player import Player
from shared.entities.food import Food
from server.client_handler import ClientThread
from server.game_manager import GameManager
from shared.packets import ServerFullPacket

logger = logging.getLogger(__name__)

class NetworkManager:
    def __init__(self, game_manager: GameManager, players: Dict[int, Player], balls: List[Food], lock: threading.RLock):
        self.game_manager = game_manager
        self.players = players
        self.balls = balls
        self.lock = lock

        self.SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.server_ip = network_cfg['host']
        self.port = network_cfg['port']
        self.max_connections = network_cfg.get('max_connections', 10)
        self.running = False
        
        self.client_threads: Dict[int, ClientThread] = {}
        self.connections = 0
        self._id = 0
        
        self.is_started = False
        self.start = False
        self.start_time = 0
        
        self.connection_attempts = {}

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
            logger.info(f"World size: {self.game_manager.world_dimensions[0]}x{self.game_manager.world_dimensions[1]}")
            
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
                            # Update all players (age and size)
                            for player in self.players.values():
                                player.update(delta_time)
                                
                            self.game_manager.update_skills()
                            self.game_manager.check_collision(self.players, self.balls)
                            self.game_manager.player_collision(self.players)
                            
                            # Maintain ball count
                            min_balls = server_cfg['ball_count']['min']
                            max_balls = server_cfg['ball_count']['max']
                            if len(self.balls) < min_balls:
                                to_add = min(max_balls - len(self.balls), max_balls - min_balls + 1)
                                if to_add > 0:
                                    self.game_manager.create_balls(to_add)
                    
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
                        server_full_packet = ServerFullPacket(message=network_cfg['protocol']['server_full_message'])
                        # Need to send length prefix manually as this is outside ClientThread
                        response_bytes = server_full_packet.to_json().encode('utf-8')
                        conn.sendall(len(response_bytes).to_bytes(4, 'big') + response_bytes)
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
                    
                    logger.info(f"New connection from {addr} (ID: {current_id})\n")
                    
            except Exception as e:
                if self.running:  # Only log if we're not shutting down
                    logger.error(f"Error in connection thread: {e}", exc_info=True)
                break