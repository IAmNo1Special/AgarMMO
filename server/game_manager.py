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
            player = self.players.get(player_id)
            if player:
                player.push_skill_active = True
                player.push_skill_end_time = time.time() + skills_cfg['push_skill']['duration']
        elif skill_name == "pull":
            player = self.players.get(player_id)
            if player:
                player.pull_skill_active = True
                player.pull_skill_end_time = time.time() + skills_cfg['pull_skill']['duration']

    def update_skills(self):
        """Update active skills with optimized collision detection"""
        current_time = time.time()
        
        with self.lock:
            for player_id, player in list(self.players.items()):
                # Update push skill
                if hasattr(player, 'push_skill_active') and player.push_skill_active:
                    if current_time > player.push_skill_end_time:
                        player.push_skill_active = False
                    else:
                        push_skill = player.skills.get('push')
                        if push_skill:
                            effective_push_radius = push_skill.radius + (player.score * skills_cfg['push_skill']['score_multiplier'])
                            # Adjust visual radius to account for player's own size, making the visual circle represent the maximum reach
                            player.push_radius = effective_push_radius + player.radius # Set push_radius for client rendering
                            push_force = push_skill.push_force
                            
                            for other_id, other_player in list(self.players.items()):
                                if player_id == other_id:
                                    continue
                                if self._is_in_skill_range(player, other_player, effective_push_radius):
                                    dx = other_player.x - player.x
                                    dy = other_player.y - player.y
                                    distance = max(1, math.sqrt(dx*dx + dy*dy))
                                    scale = push_force * (1 - (distance / effective_push_radius))
                                    other_player.x += dx * scale / distance
                                    other_player.y += dy * scale / distance
                                    self._enforce_world_boundaries(other_player)
                            
                            for ball in self.balls:
                                if self._is_in_skill_range(player, ball, effective_push_radius):
                                    dx = ball.x - player.x
                                    dy = ball.y - player.y
                                    distance = max(1, math.sqrt(dx*dx + dy*dy))
                                    scale = push_force * (1 - (distance / effective_push_radius))
                                    ball.x += dx * scale / distance
                                    ball.y += dy * scale / distance
                                    self._enforce_world_boundaries(ball)
                
                # Update pull skill
                if hasattr(player, 'pull_skill_active') and player.pull_skill_active:
                    if current_time > player.pull_skill_end_time:
                        player.pull_skill_active = False
                    else:
                        pull_skill = player.skills.get('pull')
                        if pull_skill:
                            effective_pull_radius = pull_skill.radius + (player.score * skills_cfg['pull_skill']['score_multiplier'])
                            # Adjust visual radius to account for player's own size, making the visual circle represent the maximum reach
                            player.pull_radius = effective_pull_radius + player.radius # Set pull_radius for client rendering
                            pull_force = pull_skill.pull_force
                            
                            for other_id, other_player in list(self.players.items()):
                                if player_id == other_id:
                                    continue
                                if self._is_in_skill_range(player, other_player, effective_pull_radius):
                                    dx = other_player.x - player.x
                                    dy = other_player.y - player.y
                                    distance = max(1, math.sqrt(dx*dx + dy*dy))
                                    scale = pull_force * (1 - (distance / effective_pull_radius))
                                    other_player.x -= dx * scale / distance  # Invert direction for pull
                                    other_player.y -= dy * scale / distance  # Invert direction for pull
                                    self._enforce_world_boundaries(other_player)
                            
                            for ball in self.balls:
                                if self._is_in_skill_range(player, ball, effective_pull_radius):
                                    dx = ball.x - player.x
                                    dy = ball.y - player.y
                                    distance = max(1, math.sqrt(dx*dx + dy*dy))
                                    scale = pull_force * (1 - (distance / effective_pull_radius))
                                    ball.x -= dx * scale / distance  # Invert direction for pull
                                    ball.y -= dy * scale / distance  # Invert direction for pull
                                    self._enforce_world_boundaries(ball)
    
    def _is_in_skill_range(self, obj1, obj2, skill_radius):
        """Check if two objects are within skill range of each other based on skill_radius from obj1's center"""
        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance_sq = dx*dx + dy*dy
        
        # The skill effect should only occur within the visual radius, which is skill_radius
        # from the center of obj1 (the player using the skill).
        # We also need to consider the radius of obj2, so the effective range for obj2's center
        # is skill_radius + obj2.radius
        obj2_radius = obj2.radius + (obj2.score if hasattr(obj2, 'score') else 0) # Use obj2's effective radius
        
        return distance_sq <= (skill_radius + obj2_radius) ** 2

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