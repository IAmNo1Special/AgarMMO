# `utils/config_loader.py` - Configuration Loader

This utility script provides a simple way to load configuration from YAML files.

## `load_config(config_name)` function

*   **Purpose**: To load a specified YAML configuration file from the `config/` directory.
*   **Arguments**: `config_name` (the name of the file without the `.yaml` extension).
*   **Returns**: A dictionary containing the configuration data.

## Global Configuration Variables

The script also loads all the main configuration files into global variables for easy access from other parts of the codebase. These variables are:

*   `food_cfg`
*   `game_cfg`
*   `network_cfg`
*   `player_cfg`
*   `server_cfg`
*   `skills_cfg`
*   `survival_cfg`
*   `world_cfg`

## Dependencies

*   `yaml`: For parsing YAML files.
*   `pathlib`: For creating file paths in an OS-agnostic way.
