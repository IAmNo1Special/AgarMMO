# `config/` - Game Configuration

The `config/` directory contains all the YAML configuration files for the game, allowing for easy customization of game parameters without modifying the source code.

## Files

*   **`game.yaml`**: Client-side settings, including:
    *   `fps`: Frames per second for the client.
    *   `fonts`: Font settings for the UI.
    *   `window`: Window title and initial position.
    *   `validation`: Player name length limits.
    *   `colors`: UI colors.
    *   `ui`: Positions and offsets for UI elements.

*   **`player.yaml`**: Player-specific settings:
    *   `start_radius`: The initial radius of a player.
    *   `start_velocity`: The initial movement speed of a player.
    *   `colors`: A list of possible player colors.

*   **`food.yaml`**: Food-related settings:
    *   `radius`: The radius of food pellets.
    *   `growth_amount`: The amount of score a player gains from eating a food pellet.
    *   `colors`: A list of possible food colors.

*   **`network.yaml`**: Network settings for both the client and server:
    *   `host`, `port`: The server's IP address and port.
    *   `buffer_size`, `timeout`, `max_message_size`: Low-level socket settings.
    *   `keepalive`: Settings for TCP keepalive.

*   **`server.yaml`**: Server-side settings:
    *   `max_players`: The maximum number of players allowed on the server.
    *   `ball_count`: The minimum and maximum number of food pellets on the map.

*   **`world.yaml`**: Game world settings:
    *   `screen_width`, `screen_height`: The dimensions of the client window.
    *   `world_width`, `world_height`: The dimensions of the game world.
    *   `boundary`: Settings for the world boundary (color, line width, padding).

*   **`skills.yaml`**: Configuration for player skills:
    *   `push_skill`: Settings for the "push" skill (base radius, radius per level, push force, duration, visual color, **score multiplier**, `size_threshold_multiplier`).
    *   `pull_skill`: Settings for the "pull" skill (base radius, radius per level, pull force, duration, visual color, **score multiplier**, `size_threshold_multiplier`).

*   **`survival.yaml`**: Configuration for the survival system (health, hunger, thirst, etc.).
