import random
import math
import time
import logging
from typing import Dict, List, Tuple
from threading import RLock

from shared.utils.config_loader import server_cfg, world_cfg, game_cfg, food_cfg, skills_cfg
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
                    player.increase_score(food_cfg['growth_amount'])
                    balls_to_remove.add(i)
        
        # Remove collided balls in reverse order to avoid index shifting
        for i in sorted(balls_to_remove, reverse=True):
            if i < len(balls):
                del balls[i]

    def player_collision(self, players):
        """Check for player collisions and handle them based on size."""
        player_list = list(players.values())
        
        for i, player1 in enumerate(player_list):
            for j in range(i + 1, len(player_list)):
                player2 = player_list[j]
                
                # Check if players are colliding at all
                if not player1.is_colliding(player2, require_complete_overlap=False):
                    continue
                    
                # Determine which player is larger
                if player1.radius > player2.radius:
                    larger, smaller = player1, player2
                elif player2.radius > player1.radius:
                    larger, smaller = player2, player1
                else:
                    continue  # Same size, no eating
                
                # Calculate size ratio
                size_ratio = larger.radius / smaller.radius
                
                # Only allow eating if the size difference is above the threshold
                # and the smaller player is completely inside the larger one
                if (size_ratio > game_cfg['player_eating_threshold'] and 
                    smaller.is_colliding(larger)):
                    # Larger player eats the smaller one
                    larger.increase_score(smaller.score)
                    smaller.score = 0
                    smaller.birth_time = time.time()  # Reset birth time on respawn
                    smaller.x, smaller.y = self.get_start_location(players)
                    print(f"[GAME] {larger.name} (size: {larger.radius:.1f}) ATE {smaller.name} (size: {smaller.radius:.1f})")

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
                # Update player's age and size
                player.update(current_time)

                # Update push skill
                if hasattr(player, 'push_skill_active') and player.push_skill_active:
                    if current_time > player.push_skill_end_time:
                        player.push_skill_active = False
                    else:
                        push_skill = player.skills.get('push')
                        if push_skill:
                            # Get effective radius including player size
                            effective_push_radius = push_skill.get_effective_radius(player.radius)
                            # Store for client rendering
                            player.push_radius = effective_push_radius
                            push_force = push_skill.push_force
                            
                            for other_id, other_player in list(self.players.items()):
                                if player_id == other_id:
                                    continue
                                if self._is_in_skill_range(player, other_player, effective_push_radius):
                                    dx = other_player.x - player.x
                                    dy = other_player.y - player.y
                                    distance = max(skills_cfg['push_skill'].get('min_distance', 1), math.sqrt(dx*dx + dy*dy))
                                    other_player_size = other_player.radius
                                    player_size = player.radius
                                    size_threshold = skills_cfg['push_skill']['size_threshold_multiplier']

                                    if other_player_size > player_size * size_threshold:
                                        # Object is too big, push player away
                                        min_push_force = push_skill.push_force * skills_cfg['push_skill']['min_push_force_multiplier']
                                        force_scale = skills_cfg['push_skill'].get('force_scale', 1.0)
                                        scale = max(min_push_force, push_force * (1 - (distance / effective_push_radius))) * force_scale
                                        player.x -= dx * scale / distance
                                        player.y -= dy * scale / distance
                                        self._enforce_world_boundaries(player)
                                    else:
                                        # Push object away
                                        min_push_force = push_skill.push_force * skills_cfg['push_skill']['min_push_force_multiplier']
                                        force_scale = skills_cfg['push_skill'].get('force_scale', 1.0)
                                        scale = max(min_push_force, push_force * (1 - (distance / effective_push_radius))) * force_scale
                                        other_player.x += dx * scale / distance
                                        other_player.y += dy * scale / distance
                                        self._enforce_world_boundaries(other_player)
                            
                            for ball in self.balls:
                                if self._is_in_skill_range(player, ball, effective_push_radius):
                                    size_threshold = skills_cfg['push_skill']['size_threshold_multiplier']

                                    dx = ball.x - player.x
                                    dy = ball.y - player.y
                                    distance = max(1, math.sqrt(dx*dx + dy*dy))

                                    if ball.radius > player.radius * size_threshold:
                                        # Object is too big, push player away
                                        min_push_force = push_skill.push_force * skills_cfg['push_skill']['min_push_force_multiplier']
                                        force_scale = skills_cfg['push_skill'].get('force_scale', 1.0)
                                        scale = max(min_push_force, push_force * (1 - (distance / effective_push_radius))) * force_scale
                                        player.x -= dx * scale / distance
                                        player.y -= dy * scale / distance
                                        self._enforce_world_boundaries(player)
                                    else:
                                        # Push object away
                                        min_push_force = push_skill.push_force * skills_cfg['push_skill']['min_push_force_multiplier']
                                        force_scale = skills_cfg['push_skill'].get('force_scale', 1.0)
                                        scale = max(min_push_force, push_force * (1 - (distance / effective_push_radius))) * force_scale
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
                            # Get effective radius including player size
                            effective_pull_radius = pull_skill.get_effective_radius(player.radius)
                            # Store for client rendering
                            player.pull_radius = effective_pull_radius
                            pull_force = pull_skill.pull_force
                            
                            for other_id, other_player in list(self.players.items()):
                                if player_id == other_id:
                                    continue
                                if self._is_in_skill_range(player, other_player, effective_pull_radius):
                                    size_threshold = skills_cfg['pull_skill']['size_threshold_multiplier']

                                    if not (other_player.radius > player.radius * size_threshold):
                                        # Only pull if not too big
                                        dx = other_player.x - player.x
                                        dy = other_player.y - player.y
                                        distance = max(1, math.sqrt(dx*dx + dy*dy))
                                        force_scale = skills_cfg['pull_skill'].get('force_scale', 1.0)
                                        scale = pull_force * (1 - (distance / effective_pull_radius)) * force_scale
                                        other_player.x -= dx * scale / distance  # Invert direction for pull
                                        other_player.y -= dy * scale / distance  # Invert direction for pull
                                        self._enforce_world_boundaries(other_player)
                            
                            for ball in self.balls:
                                if self._is_in_skill_range(player, ball, effective_pull_radius):
                                    size_threshold = skills_cfg['pull_skill']['size_threshold_multiplier']

                                    dx = ball.x - player.x
                                    dy = ball.y - player.y
                                    distance = max(1, math.sqrt(dx*dx + dy*dy))

                                    if not (ball.radius > player.radius * size_threshold):
                                        # Only pull if not too big
                                        force_scale = skills_cfg['pull_skill'].get('force_scale', 1.0)
                                        scale = pull_force * (1 - (distance / effective_pull_radius)) * force_scale
                                        ball.x -= dx * scale / distance  # Invert direction for pull
                                        ball.y -= dy * scale / distance  # Invert direction for pull
                                        self._enforce_world_boundaries(ball)
    
    def _is_in_skill_range(self, obj1, obj2, skill_radius):
        """Check if obj2 is within skill_radius of obj1.
        
        Args:
            obj1: The source object (player using the skill)
            obj2: The target object to check
            skill_radius: The total radius of the skill effect (including player radius)
            
        Returns:
            bool: True if obj2 is within the skill's effective range
        """
        dx = obj1.x - obj2.x
        dy = obj1.y - obj2.y
        distance_sq = dx*dx + dy*dy
        
        # Check if the distance between centers is less than the sum of skill radius and target radius
        return distance_sq <= (skill_radius + obj2.radius) ** 2

    def _enforce_world_boundaries(self, game_object):
        """Ensure a game object stays within the world boundaries"""
        padding = world_cfg['boundary']['padding']
        world_w, world_h = self.world_dimensions
        game_object.x = max(padding + game_object.radius, min(game_object.x, world_w - padding - game_object.radius))
        game_object.y = max(padding + game_object.radius, min(game_object.y, world_h - padding - game_object.radius))

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
                if dis <= self.player_start_radius + player.radius + padding:
                    valid_position = False
                    break
            if valid_position:
                return (x, y)
        return (random.randint(padding, world_w - padding), random.randint(padding, world_h - padding))

    def get_serializable_players(self):
        """Convert Player objects to a serializable dictionary"""
        return {pid: p.to_dict() for pid, p in self.players.items()}