# `shared/entities/` - Game Entities

The `shared/entities/` directory contains the data models for all objects in the game.

## `game_object.py`

* **`GameObject` class**: A base class for all game objects.
  * **Attributes**: `x`, `y`, `radius`, `color`, `object_type`.
  * **Methods**:
    * `is_colliding(other)`: Checks for collision with another `GameObject`, accounting for effective radius (including score for players).
    * `to_dict()`: Returns a dictionary representation of the object.

## `player.py`

* **`Player` class**: Represents a player in the game.
  * **Attributes**: Inherits from `GameObject` (implicitly) and adds `id`, `name`, `score`, `start_velocity`, `skills`, and survival stats.
  * **Methods**:
    * `move()`: Updates the player's position.
    * `grow()`: Increases the player's score.
    * `to_dict()`: Serializes the player's data.

## `food.py`

* **`Food` class**: Represents a food pellet.
  * Inherits from `GameObject`.
  * Has a `to_dict()` method for serialization.

## `survival.py`

* **`SurvivalStats` class**: A dataclass to hold survival-related stats (health, calories, etc.).
* **`SurvivalSystem` class**: Contains the server-side logic for updating survival stats. This system is not fully integrated into the main game loop yet.

## `skills/push.py`

* **`PushSkill` class**: Defines the "push" skill, including its radius and force.
