from shared.utils.config_loader import skills_cfg

class PullSkill:
    def __init__(self, level=1):
        self.level = level
        self.base_radius = skills_cfg['pull_skill']['base_radius']
        self.radius_per_level = skills_cfg['pull_skill']['radius_per_level']
        self.pull_force = skills_cfg['pull_skill']['pull_force']
        self.duration = skills_cfg['pull_skill']['duration']

    @property
    def radius(self):
        """Returns the base skill radius without player size"""
        return self.base_radius + (self.level - 1) * self.radius_per_level
        
    def get_effective_radius(self, player_radius):
        """Returns the total radius including the player's radius"""
        return self.radius + player_radius