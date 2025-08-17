from utils.config_loader import skills_cfg

class PushSkill:
    def __init__(self, level=1):
        self.level = level
        self.base_radius = skills_cfg['push_skill']['base_radius']
        self.radius_per_level = skills_cfg['push_skill']['radius_per_level']
        self.push_force = skills_cfg['push_skill']['push_force']

    @property
    def radius(self):
        return self.base_radius + (self.level - 1) * self.radius_per_level
