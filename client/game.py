import contextlib
import os
import time
import pygame
from client.network import Network
from shared.config_loader import player_cfg, world_cfg, game_cfg, food_cfg, skills_cfg
from client.rendering.game_renderer import GameRenderer
from client.rendering.ui_renderer import UIRenderer
from client.input_handler import InputHandler
from shared.packets import PlayerIdPacket, UsernameTakenPacket, ServerFullPacket, GameStatePacket, ConnectPacket

class Game:
    def __init__(self):
        # Initialize pygame
        with contextlib.redirect_stdout(None):
            pygame.init()

        # Load configuration
        self._load_game_config()
        
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

        # Initialize renderers
        self.game_renderer = GameRenderer(
            WIN=self.WIN,
            players=self.players,
            balls=self.balls,
            camera_x=self.camera_x,
            camera_y=self.camera_y,
            W=self.W,
            H=self.H,
            WORLD_W=self.WORLD_W,
            WORLD_H=self.WORLD_H,
            PLAYER_RADIUS=self.PLAYER_RADIUS,
            BALL_RADIUS=self.BALL_RADIUS,
            NAME_FONT=self.NAME_FONT,
            PLAYER_COLORS=self.PLAYER_COLORS,
            FOOD_COLORS=self.FOOD_COLORS
        )
        self.ui_renderer = UIRenderer(
            WIN=self.WIN,
            players=self.players,
            game_time=self.game_time,
            W=self.W,
            H=self.H,
            TIME_FONT=self.TIME_FONT,
            SCORE_FONT=self.SCORE_FONT
        )

        # Initialize input handler
        self.input_handler = InputHandler(
            current_id=self.current_id,
            players=self.players,
            server=self.server,
            W=self.W,
            H=self.H,
            PLAYER_RADIUS=self.PLAYER_RADIUS,
            START_VEL=self.START_VEL
        )
    
    def _load_game_config(self):
        """Load game configuration from config files"""
        # Screen and world dimensions
        self.W, self.H = world_cfg['screen_width'], world_cfg['screen_height']
        self.WORLD_W, self.WORLD_H = world_cfg['world_width'], world_cfg['world_height']
        self.BOUNDARY_PADDING = world_cfg['boundary']['padding']
        
        # Game constants
        self.PLAYER_RADIUS = player_cfg['size']['newborn']  # Use newborn size as starting radius
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
        # Set window position from config before creating the window
        window_x, window_y = game_cfg['window']['initial_position']
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{window_x},{window_y}"
        
        # Initialize window with hardware acceleration and double buffering
        self.WIN = pygame.display.set_mode(
            (self.W, self.H),
            pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        
        # Set window title
        pygame.display.set_caption(game_cfg['window']['title'])
        
        # Enable alpha blending for transparency
        self.WIN.set_alpha(None)

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
        try:
            if self.server.connect(name):
                self.current_id = self.server.get_player_id()
                # Update input handler with current_id and server
                self.input_handler.current_id = self.current_id
                self.input_handler.server = self.server
                return self.current_id is not None
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_game_state(self):
        """Get the current game state from server"""
        game_state_data = self.server.get_game_state()
        if not game_state_data:
            return False
            
        self.balls.clear() # Clear existing items
        self.balls.extend(game_state_data.get("balls", [])) # Add new items
        
        # Update game state
        self.players.clear()  # Clear existing items
        self.players.update(game_state_data.get("players", {}))  # Update with new items
        self.game_time = game_state_data.get("game_time", 0)
        return True
    
    def draw(self):
        """Draw the game state"""
        if self.current_id not in self.players:
            return
            
        player = self.players[self.current_id]
        
        # Update camera to follow player
        # Update camera to follow player, clamping to world boundaries
        camera_x_unclamped = player["x"] - self.W // 2
        camera_y_unclamped = player["y"] - self.H // 2

        # Clamp camera_x
        self.game_renderer.camera_x = max(0, min(camera_x_unclamped, self.WORLD_W - self.W))
        # Clamp camera_y
        self.game_renderer.camera_y = max(0, min(camera_y_unclamped, self.WORLD_H - self.H))
        
        # Draw game objects
        self.game_renderer.draw()
        
        # Update UI renderer with current game state
        self.ui_renderer.game_time = self.game_time
        self.ui_renderer.players = self.players
        self.ui_renderer.draw_ui(player["score"], player["age"], player["growth_percentage"])
        
        

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
            
        # Initialize timing
        last_update = time.time()
        update_interval = 1.0 / 60.0  # 60 FPS
        
        # Main game loop
        self.running = True
        while self.running:
            current_time = time.time()
            delta_time = current_time - last_update
            
            # Update game state at a fixed interval
            if delta_time >= update_interval:
                last_update = current_time
                
                # Handle input events and check for quit
                if not self.input_handler.handle_events():
                    self.running = False
                    break
                    
                # Handle player movement
                self.input_handler.handle_movement()
                
                # Get updated game state
                if not self.get_game_state():
                    print("Failed to get updated game state")
                    break
                
                # Draw the game
                self.draw()
                pygame.display.flip() # Perform the actual display update here
                
            # Cap the frame rate
            self.clock.tick(120)  # Higher tick rate for smoother input handling
    
    def cleanup(self):
        """Clean up resources"""
        if self.server:
            self.server.disconnect()
        pygame.quit()