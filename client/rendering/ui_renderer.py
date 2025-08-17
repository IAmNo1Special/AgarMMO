import pygame
from typing import Dict, List, Tuple, Any

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

    def draw_ui(self, player_score):
        """Draw the user interface"""
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
        
        # Draw time and score
        time_text = self.TIME_FONT.render(
            f"Time: {self.convert_time(self.game_time)}", 
            1, 
            (0, 0, 0)
        )
        self.WIN.blit(time_text, game_cfg['ui']['time_display_position'])
        
        score_text = self.TIME_FONT.render(
            f"Score: {round(player_score)}", 
            1, 
            (0, 0, 0)
        )
        self.WIN.blit(score_text, (game_cfg['ui']['score_display_position_x'], game_cfg['ui']['score_display_offset_y'] + score_text.get_height()))
