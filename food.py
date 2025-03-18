import os
import json
import time
import math
import random
from typing import List, Optional
from ursina import Vec3, Entity, destroy, color

#--- Configuration ---
# Load config first
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)
# Set confguration variables
map_size = config['map_size']

class Food:
    """Class representing edible resources in the environment"""
    instances: List['Food'] = []
    # Set confguration variables
    map_size = config['map_size']
    food_spawn_rate = config['food_spawn_rate']

    def __init__(self, position: Optional[Vec3] = None):
        self.energy_value: int = 50
        self.start_time = time.time()
        self.entity: Entity = Entity(
            model='sphere',
            color=color.green,
            scale=0.2,
            position=position or self.random_position(),
            collider='sphere',
            texture='white_cube'
        )
        Food.instances.append(self)

    def random_position(self):
        return Vec3(
            random.uniform(-map_size + 1, map_size - 1),
            0.5,
            random.uniform(-map_size + 1, map_size - 1)
        )

    def update(self):  # Add this new method
        # Bouncing animation using sine wave
        t = time.time() - self.start_time
        self.entity.y = 0.8 + (math.sin(t * 3) * 0.2)
        
        # Spinning animation
        self.entity.rotation_y += 50 * time.dt

    def destroy(self):
        if hasattr(self, 'entity') and self.entity:
            destroy(self.entity)  # Destroy the entity
            self.entity = None  # Clear the reference
        if self in Food.instances:
            Food.instances.remove(self)  # Remove from the instances list