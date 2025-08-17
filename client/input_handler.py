import pygame
from typing import Dict, Any

from shared.config_loader import game_cfg

class InputHandler:
    def __init__(self, current_id: str, players: Dict[str, Any], server: Any, W: int, H: int, PLAYER_RADIUS: int, START_VEL: int):
        self.current_id = current_id
        self.players = players
        self.server = server
        self.W = W
        self.H = H
        self.PLAYER_RADIUS = PLAYER_RADIUS
        self.START_VEL = START_VEL

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.server.send("push")
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def handle_movement(self):
        """Handle player movement input"""
        if self.current_id not in self.players:
            return
            
        player = self.players[self.current_id]
        vel = max(game_cfg['min_velocity'], self.START_VEL - round(player["score"]/game_cfg['player_velocity_score_divisor']))
        
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        # Calculate movement vector
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= game_cfg['diagonal_movement_factor']
            dy *= game_cfg['diagonal_movement_factor']
            
        # Only send movement if any key is pressed
        if dx != 0 or dy != 0:
            self.server.send(f"move {dx} {dy}")
