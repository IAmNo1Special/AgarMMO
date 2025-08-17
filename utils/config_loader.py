"""Utility functions for loading configuration files."""

import yaml
from pathlib import Path
from typing import Any, Dict


def load_config(config_name: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file from the config directory.
    
    Args:
        config_name: Name of the config file (without .yaml extension)
        
    Returns:
        Dict containing the configuration data
    """
    config_dir = Path(__file__).parent.parent / 'config'
    config_path = config_dir / f"{config_name}.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# Load common configurations
food_cfg = load_config('food')
game_cfg = load_config('game')
network_cfg = load_config('network')
player_cfg = load_config('player')
server_cfg = load_config('server')
skills_cfg = load_config('skills')
survival_cfg = load_config('survival')
world_cfg = load_config('world')

