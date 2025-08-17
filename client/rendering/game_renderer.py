import pygame
from typing import Dict, List, Tuple, Any

from shared.config_loader import game_cfg, world_cfg, skills_cfg

class GameRenderer:
    def __init__(self, WIN: pygame.Surface, players: Dict[str, Any], balls: List[Any], camera_x: int, camera_y: int, W: int, H: int, WORLD_W: int, WORLD_H: int, PLAYER_RADIUS: int, BALL_RADIUS: int, NAME_FONT: pygame.font.Font, PLAYER_COLORS: List[Tuple[int, int, int]], FOOD_COLORS: List[Tuple[int, int, int]]):
        self.WIN = WIN
        self.players = players
        self.balls = balls
        self.camera_x = camera_x
        self.camera_y = camera_y
        self.W = W
        self.H = H
        self.WORLD_W = WORLD_W
        self.WORLD_H = WORLD_H
        self.PLAYER_RADIUS = PLAYER_RADIUS
        self.BALL_RADIUS = BALL_RADIUS
        self.NAME_FONT = NAME_FONT
        self.PLAYER_COLORS = PLAYER_COLORS
        self.FOOD_COLORS = FOOD_COLORS

    def draw(self):
        """Draw the game state"""
        # Clear screen
        self.WIN.fill(game_cfg['colors']['background'])
        
        # Draw game elements
        self.draw_boundary()
        self.draw_balls()
        self.draw_players()
        
        # Update display
        pygame.display.flip()
    
    def draw_boundary(self):
        """Draw the game world boundary"""
        boundary_rect = pygame.Rect(
            -self.camera_x, 
            -self.camera_y, 
            self.WORLD_W, 
            self.WORLD_H
        )
        pygame.draw.rect(self.WIN, world_cfg['boundary']['color'], boundary_rect, world_cfg['boundary']['line_width'])
    
    def draw_balls(self):
        """Draw all visible food balls"""
        for ball in self.balls:
            ball_x, ball_y = ball['x'] - self.camera_x, ball['y'] - self.camera_y
            
            # Only draw if ball is in view
            if (-self.BALL_RADIUS < ball_x < self.W + self.BALL_RADIUS and 
                -self.BALL_RADIUS < ball_y < self.H + self.BALL_RADIUS):
                pygame.draw.circle(
                    self.WIN, 
                    tuple(ball['color']), 
                    (int(ball_x), int(ball_y)), 
                    self.BALL_RADIUS
                )
    
    def draw_players(self):
        """Draw all players"""
        for p_id in sorted(self.players, key=lambda x: self.players[x]["score"]):
            p = self.players[p_id]
            draw_x = p["x"] - self.camera_x
            draw_y = p["y"] - self.camera_y
            
            # Draw player circle
            pygame.draw.circle(
                self.WIN, 
                p["color"], 
                (draw_x, draw_y), 
                self.PLAYER_RADIUS + round(p["score"])
            )
            
            # Draw push radius if active
            if p.get('push_skill_active', False):
                push_radius = p.get('push_radius', 0)
                if push_radius > 0:
                    surface = pygame.Surface(
                        (push_radius * 2, push_radius * 2), 
                        pygame.SRCALPHA
                    )
                    pygame.draw.circle(
                        surface, 
                        skills_cfg['push_skill']['visual_color'], 
                        (push_radius, push_radius), 
                        push_radius
                    )
                    self.WIN.blit(surface, (draw_x - push_radius, draw_y - push_radius))
            
            # Draw player name
            text = self.NAME_FONT.render(p["name"], game_cfg['fonts']['antialiasing'], game_cfg['colors']['text'])
            name_x = draw_x - text.get_width() / 2
            name_y = draw_y - text.get_height() / 2 - (self.PLAYER_RADIUS + round(p["score"]) + game_cfg['ui']['player_name_offset_y'])
            self.WIN.blit(text, (name_x, name_y))
