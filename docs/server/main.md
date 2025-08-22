# Server Main Module

The `main.py` file serves as the entry point for the AgarMMO game server, initializing all core components and starting the server.

## Overview

This module is responsible for:

- Initializing the game world and state
- Setting up the game manager
- Configuring the network manager
- Starting the server's main loop

## Components

### Game State

- `players` (Dict[str, Player]): Active players by ID
- `foods` (List[Food]): List of food items in the game
- `lock` (threading.RLock): Thread synchronization lock
- `world_width` (int): World width in pixels
- `world_height` (int): World height in pixels
- `player_radius` (int): Base player radius
- `food_radius` (int): Food item radius
- `player_colors` (List[Tuple[int, int, int]]): Available player colors

### Game Manager

Manages core game logic including:

- Player interactions
- Food spawning and consumption
- Game state updates
- Collision detection

### Network Manager

Handles all network operations:

- Client connections
- Message routing
- Game state synchronization
- Network error handling

## Execution Flow

### 1. Initialization Phase

- Load configuration from YAML files
- Set up logging with appropriate log levels
- Initialize empty game state
- Configure world and player properties

### 2. Component Setup

- Create game manager with initial state
- Initialize network manager with game manager reference
- Set up network socket for client connections
- Initialize thread synchronization primitives

### 3. Server Startup

- Begin accepting client connections
- Start main server loop
- Handle graceful shutdown on termination signals
- Clean up resources on exit

## Configuration

Loaded from YAML configuration files:

- `world_cfg`: World dimensions and boundaries
- `player_cfg`: Player properties and colors
- `network_cfg`: Network settings (via NetworkManager)
- `game_cfg`: Game mechanics (via GameManager)

## Dependencies

### Standard Library

- `threading`: For thread synchronization
- `logging`: For server logging
- `signal`: For graceful shutdown handling
- `sys`: For system-level operations

### Project Modules

- `shared.utils.config_loader`: Configuration management
- `shared.entities.player`: Player class definition
- `shared.entities.food`: Food class definition
- `server.game_manager`: Game logic implementation
- `server.network_manager`: Network handling

## Error Handling

- Global exception handler for uncaught exceptions
- Graceful shutdown on critical errors
- Comprehensive error logging
- Resource cleanup on exit

## Logging

### Log Levels

- `DEBUG`: Detailed debug information
- `INFO`: General server events
- `WARNING`: Non-critical issues
- `ERROR`: Recoverable errors
- `CRITICAL`: Fatal errors requiring shutdown

### Log Format

```plaintext
[YYYY-MM-DD HH:MM:SS,MMM] [LEVEL] [MODULE] Message
```

## Thread Safety

- Uses `RLock` for thread synchronization
- Implements proper resource cleanup
- Handles concurrent access to shared state
- Manages thread lifecycles

## Usage

### Starting the Server

```bash
python server/main.py
```

### Command Line Arguments

- `--config`: Path to custom configuration directory (optional)
- `--debug`: Enable debug logging
- `--port`: Override default server port

## Monitoring

Server exposes the following metrics:

- Active connections
- Player count
- Game tick rate
- Memory usage
- Network throughput
