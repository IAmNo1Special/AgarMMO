import contextlib
import os
import time
import pygame
from network import Network
from utils.config_loader import player_cfg, world_cfg, game_cfg, food_cfg

class Game:
    def __init__(self):
        # Initialize pygame
        with contextlib.redirect_stdout(None):
            pygame.init()

        # Load configuration
        self.load_config()
        
        # Game state
        self.players = {}
        self.balls = []
        self.camera_x = 0
        self.camera_y = 0
        self.current_id = None
        self.server = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.game_time = 0
        
        # Initialize window
        self.init_window()
    
    def load_config(self):
        """Load game configuration from config files"""
        # Screen and world dimensions
        self.W, self.H = world_cfg['screen_width'], world_cfg['screen_height']
        self.WORLD_W, self.WORLD_H = world_cfg['world_width'], world_cfg['world_height']
        self.BOUNDARY_PADDING = world_cfg['boundary']['padding']
        
        # Game constants
        self.PLAYER_RADIUS = player_cfg['start_radius']
        self.START_VEL = player_cfg['start_velocity']
        self.BALL_RADIUS = food_cfg['radius']
        
        # Load fonts
        self.NAME_FONT = pygame.font.SysFont(
            game_cfg['fonts']['name_font']['name'],
            game_cfg['fonts']['name_font']['size']
        )
        self.TIME_FONT = pygame.font.SysFont(
            game_cfg['fonts']['time_font']['name'],
            game_cfg['fonts']['time_font']['size']
        )
        self.SCORE_FONT = pygame.font.SysFont(
            game_cfg['fonts']['score_font']['name'],
            game_cfg['fonts']['score_font']['size']
        )
        
        # Colors
        self.PLAYER_COLORS = [tuple(color) for color in player_cfg['colors']]
        self.FOOD_COLORS = [tuple(color) for color in food_cfg['colors']]
    
    def init_window(self):
        """Initialize the game window"""
        self.WIN = pygame.display.set_mode((self.W, self.H))
        
        # Set window position from config
        window_x, window_y = game_cfg['window']['initial_position']
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{window_x},{window_y}"
        pygame.display.set_caption(game_cfg['window']['title'])

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


    def connect_to_server(self, name):
        """Connect to the game server"""
        self.server = Network()
        if self.server.connect(name):
            self.current_id = self.server.get_player_id()
            return self.current_id is not None
        return False
    
    def get_game_state(self):
        """Get the current game state from server"""
        game_state = self.server.get_game_state()
        if not isinstance(game_state, dict):
            return False
            
        self.balls = game_state.get("balls", [])
        self.players = game_state.get("players", {})
        self.game_time = game_state.get("game_time", 0)
        return True
    
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
    
    def draw(self):
        """Draw the game state"""
        if self.current_id not in self.players:
            return
            
        player = self.players[self.current_id]
        
        # Update camera to follow player
        self.camera_x = player["x"] - self.W // 2
        self.camera_y = player["y"] - self.H // 2
        
        # Clear screen
        self.WIN.fill(game_cfg['colors']['background'])
        
        # Draw game elements
        self.draw_boundary()
        self.draw_balls()
        self.draw_players()
        self.draw_ui(player["score"])
        
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
    
    def run(self, player_name):
        """Run the main game loop"""
        # Connect to server
        if not self.connect_to_server(player_name):
            print("Failed to connect to server")
            return
        
        # Get initial game state
        if not self.get_game_state():
            print("Failed to get initial game state")
            return
        
        # Main game loop
        self.running = True
        while self.running:
            # Handle events
            self.running = self.handle_events()
            
            # Update game state
            if not self.get_game_state():
                print("Error getting game state")
                break
            
            # Handle movement
            self.handle_movement()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(game_cfg['fps'])
        
        # Clean up
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.server:
            self.server.disconnect()
        pygame.quit()

