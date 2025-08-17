import random
import math
import time
import logging
from typing import Dict, List, Set, Tuple, Optional
from threading import RLock

from shared.config_loader import server_cfg, world_cfg, player_cfg, game_cfg, food_cfg, skills_cfg
from shared.entities.player import Player
from shared.entities.food import Food

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self, players: Dict[int, Player], balls: List[Food], world_dimensions: Tuple[int, int], player_start_radius: int, player_colors: List[Tuple[int, int, int]], lock: RLock, start: bool, start_time: float):
        self.players = players
        self.balls = balls
        self.world_dimensions = world_dimensions
        self.player_start_radius = player_start_radius
        self.player_colors = player_colors
        self.lock = lock
        self.start = start
        self.start_time = start_time
        
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
                base_push_radius = getattr(push_skill, 'radius', skills_cfg['push_skill']['base_radius'])
                effective_push_radius = base_push_radius + (player.score * skills_cfg['push_skill']['score_multiplier'])
                
                # Calculate push force based on skill level
                push_force = getattr(push_skill, 'push_force', skills_cfg['push_skill']['push_force'])
                
                # Check collisions with other players
                for other_id, other_player in list(self.players.items()):
                    if player_id == other_id:
                        continue
                        
                    if self._is_in_in_push_range(player, other_player, effective_push_radius):
                        # Calculate push direction and apply force
                        dx = other_player.x - player.x
                        dy = other_player.y - player.y
                        distance = max(1, math.sqrt(dx*dx + dy*dy))
                        
                        # Normalize and scale by push force
                        scale = push_force * (1 - (distance / effective_push_radius))
                        other_player.x += dx * scale / distance
                        other_player.y += dy * scale / distance
                        self._enforce_world_boundaries(other_player)
                
                # Check collisions with balls
                for ball in self.balls:
                    if self._is_in_push_range(player, ball, effective_push_radius):
                        dx = ball.x - player.x
                        dy = ball.y - player.y
                        distance = max(1, math.sqrt(dx*dx + dy*dy))
                        
                        # Normalize and scale by push force
                        scale = push_force * (1 - (distance / effective_push_radius))
                        ball.x += dx * scale / distance
                        ball.y += dy * scale / distance
                        self._enforce_world_boundaries(ball)
    
    def _is_in_push_range(self, obj1, obj2, push_radius):
        """Check if two objects are within push range of each other"""
        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance_sq = dx*dx + dy*dy
        
        obj1_effective_radius = obj1.radius + (obj1.score if hasattr(obj1, 'score') else 0)
        obj2_effective_radius = obj2.radius + (obj2.score if hasattr(obj2, 'score') else 0)
        
        max_distance = (obj1_effective_radius + obj2_effective_radius + push_radius) ** 2
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