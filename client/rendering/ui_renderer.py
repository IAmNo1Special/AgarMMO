import pygame
from typing import Dict, Any

from shared.config_loader import game_cfg

class UIRenderer:
    def __init__(self, WIN: pygame.Surface, players: Dict[str, Any], game_time: int, W: int, H: int, TIME_FONT: pygame.font.Font, SCORE_FONT: pygame.font.Font):
        self.WIN = WIN
        self.players = players
        self.game_time = game_time
        self.W = W
        self.H = H
        self.TIME_FONT = TIME_FONT
        self.SCORE_FONT = SCORE_FONT

    @staticmethod
    def convert_time(t):
        """Convert seconds to MM:SS format"""
        if isinstance(t, str):
            return t
        
        t = int(t)
        if t < 60:
            return f"{t}s"
            
        minutes = t // 60
        seconds = t % 60
        return f"{minutes}:{seconds:02d}"

    def draw_ui(self, player_score, player_age, growth_percentage):
        """Draw the user interface with player stats and game info
        
        Args:
            player_score: The current player's score
            player_age: The current player's age in seconds
            growth_percentage: The current player's growth percentage (0-100)
        """
        # Ensure we have valid values
        player_age = player_age or 0
        growth_percentage = growth_percentage or 0
        
        # Check if we need to redraw the UI
        current_state = {
            'score': round(player_score),
            'age': round(player_age),
            'growth': round(growth_percentage)
        }

        # Draw scoreboard
        sorted_players = sorted(
            self.players.items(), 
            key=lambda x: x[1]["score"], 
            reverse=True
        )
        
        # Draw scoreboard title
        title = self.TIME_FONT.render("Scoreboard", 1, (0, 0, 0))
        start_y = game_cfg['ui']['scoreboard_start_y']
        x = self.W - title.get_width() - game_cfg['ui']['scoreboard_offset_x']
        self.WIN.blit(title, (x, game_cfg['ui']['scoreboard_title_offset_y']))
        
        # Draw top 3 players
        for count, (p_id, p) in enumerate(sorted_players[:3]):
            text = self.SCORE_FONT.render(
                f"{count+1}. {p['name']}", 
                game_cfg['fonts']['antialiasing'], 
                game_cfg['colors']['text']
            )
            self.WIN.blit(text, (x, start_y + count * 20))
        
        # Draw player stats on the left side
        stat_y = 30  # Increased from 10 to avoid top of screen
        stat_x = 20  # Increased from 10 for better visibility
        line_height = 30  # Increased from 25 for better spacing
        
        # World Age with background for better visibility
        world_age_surface = self.SCORE_FONT.render(
            f"World Age: {self.convert_time(self.game_time)}",
            game_cfg['fonts']['antialiasing'],
            (255, 255, 255)  # White text
        )
        # Create a surface for the background with per-pixel alpha
        bg_surface = pygame.Surface((world_age_surface.get_width() + 10, 
                                   world_age_surface.get_height() + 4), 
                                  pygame.SRCALPHA)
        # Fill with semi-transparent black
        bg_surface.fill((0, 0, 0, 180))
        # Blit the background surface
        self.WIN.blit(bg_surface, (stat_x - 5, stat_y - 2))
        self.WIN.blit(world_age_surface, (stat_x, stat_y))
        
        # Player Age with background
        player_age_surface = self.SCORE_FONT.render(
            f"Your Age: {self.convert_time(player_age)}",
            game_cfg['fonts']['antialiasing'],
            (255, 255, 255)  # White text
        )
        # Create a surface for the background with per-pixel alpha
        bg_surface = pygame.Surface((player_age_surface.get_width() + 10, 
                                   player_age_surface.get_height() + 4), 
                                  pygame.SRCALPHA)
        # Fill with semi-transparent black
        bg_surface.fill((0, 0, 0, 180))
        # Blit the background surface
        self.WIN.blit(bg_surface, (stat_x - 5, stat_y + line_height - 2))
        self.WIN.blit(player_age_surface, (stat_x, stat_y + line_height))
        
        # Growth Percentage with background
        growth_surface = self.SCORE_FONT.render(
            f"Growth: {min(100, int(growth_percentage))}%",
            game_cfg['fonts']['antialiasing'],
            (255, 255, 255)  # White text
        )
        # Create a surface for the background with per-pixel alpha
        bg_surface = pygame.Surface((growth_surface.get_width() + 10, 
                                   growth_surface.get_height() + 4), 
                                  pygame.SRCALPHA)
        # Fill with semi-transparent black
        bg_surface.fill((0, 0, 0, 180))
        # Blit the background surface
        self.WIN.blit(bg_surface, (stat_x - 5, stat_y + line_height * 2 - 2))
        self.WIN.blit(growth_surface, (stat_x, stat_y + line_height * 2))
        
        # Draw growth bar
        bar_width = 200
        bar_height = 10
        border = 2
        
        # Draw border
        pygame.draw.rect(self.WIN, (0, 0, 0), 
                       (stat_x - border, stat_y + line_height * 3 - border, 
                        bar_width + 2 * border, bar_height + 2 * border))
        
        # Draw background
        pygame.draw.rect(self.WIN, (200, 200, 200), 
                       (stat_x, stat_y + line_height * 3, 
                        bar_width, bar_height))
        
        # Draw filled portion
        fill_width = int(bar_width * (growth_percentage / 100))
        if fill_width > 0:
            # Gradient from red to green based on growth percentage
            r = int(255 * (1 - growth_percentage/100))
            g = int(255 * (growth_percentage/100))
            pygame.draw.rect(self.WIN, (r, g, 0), 
                           (stat_x, stat_y + line_height * 3, 
                            fill_width, bar_height))
        
        # Draw score at bottom left
        score_text = self.SCORE_FONT.render(
            f"Score: {round(player_score)}", 
            game_cfg['fonts']['antialiasing'],
            (0, 0, 0)
        )
        self.WIN.blit(score_text, (stat_x, self.H - 30))
