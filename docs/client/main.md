# Client Main Module

The `main.py` file serves as the entry point for the AgarMMO game client, handling initialization and the main game loop.

## Overview

This module is responsible for:

- Initializing the Pygame environment
- Collecting and validating player input
- Starting the main game loop
- Handling application shutdown

## Main Execution Flow

1. **Pygame Initialization**
   - Suppresses Pygame's welcome message
   - Initializes all Pygame modules

2. **Player Name Collection**
   - Loads name validation rules from game configuration
   - Prompts user for a player name
   - Validates name length against configured limits
   - Re-prompts if validation fails

3. **Game Initialization**
   - Creates a new `Game` instance
   - Starts the game with the provided player name

4. **Error Handling**
   - Catches and displays any exceptions that occur
   - Ensures Pygame is properly cleaned up on exit

## Configuration

Uses the following configuration from `game_cfg`:

```yaml
validation:
  min_name_length: 3    # Minimum allowed characters in player name
  max_name_length: 20   # Maximum allowed characters in player name
```

## Dependencies

### Standard Library

- `contextlib`: For suppressing Pygame's welcome message

### Third-Party

- `pygame`: Game development library

### Project Modules

- `client.game`: Main game class
- `shared.utils.config_loader`: Game configuration
