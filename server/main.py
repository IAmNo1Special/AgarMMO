import threading
import logging
from typing import Dict, List
from shared.config_loader import world_cfg, player_cfg

from shared.entities.player import Player
from shared.entities.food import Food
from server.game_manager import GameManager
from server.network_manager import NetworkManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    players: Dict[int, Player] = {}
    balls: List[Food] = []
    lock = threading.RLock()
    start = False
    start_time = 0

    world_dimensions = (world_cfg['world_width'], world_cfg['world_height'])
    player_start_radius = player_cfg['size']['newborn']  # Use newborn size as starting radius
    player_colors = [tuple(color) for color in player_cfg['colors']]

    game_manager = GameManager(
        players=players,
        balls=balls,
        world_dimensions=world_dimensions,
        player_start_radius=player_start_radius,
        player_colors=player_colors,
        lock=lock,
        start=start,
        start_time=start_time
    )

    network_manager = NetworkManager(
        game_manager=game_manager,
        players=players,
        balls=balls,
        lock=lock
    )

    if network_manager.connect_server():
        network_manager.mainloop()
