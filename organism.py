#organism.py
import os
import json
from typing import List, Optional, TYPE_CHECKING
from ursina import *
from genomics import Genome
import math
import random
import time
from food import Food
debug=True
#--- Configuration ---
# Load config first
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)
# Set confguration variables
energy_cost_per_meter = config['energy_cost_per_meter']

class Organism:
    """Class representing autonomous biological entities"""
    instances: List['Organism'] = []
    selected_organism = None  # Class-level tracking
    HOVER_COLOR = color.Color(1, 1, 0, 0.5)  # 50% transparent yellow
    def __init__(
        self,
        position: Vec3 = Vec3(0, 0, 0),
        genome: Optional[Genome] = None,
        color: color.Color = color.lime
    ):
        self.genome = genome or Genome.random_genome()
        self.default_energy = self.genome.express_trait('default_energy')
        self.energy: int = self.default_energy
        self.mating_mode: bool = False
        self.target_food: Optional['Food'] = None
        self.last_position: Vec3 = Vec3(position.x, position.y, position.z)  # Fixed copy
        

        self.wander_target = None
        self.next_wander_time = 0
        self.wander_duration = 1.5  # How long to move in one direction
        self.wander_speed_multiplier = 1  # Slower movement when wandering
        # Expressed traits
        self.sight_fov = math.radians(self.genome.express_trait('sight_fov'))
        self.sight_range = self.genome.express_trait('sight_range')
        self.strength = self.genome.express_trait('strength')
        self.speed = self.genome.express_trait('speed')
        self.size = self.genome.express_trait('size')
        
        # Initialize entity
        self.min_height = 0.7  # Minimum height above the ground
        self.max_height = 1.5  # Maximum height above the ground
        self.entity = Entity(
            position=position,
            model='sphere',
            color=color,
            scale=self.size,
            collider='sphere',
            texture='white_cube'
        )
        self.original_color = color
        self._add_eyes()
        Organism.instances.append(self)
        # Click detection for on_select(self)
        self.entity.collider = 'sphere'
        self.entity.on_click = self.on_select
        self.is_selected = False

    def on_select(self):
        # Deselect previous organism
        if Organism.selected_organism:
            Organism.selected_organism.is_selected = False
            Organism.selected_organism.entity.color = Organism.selected_organism.original_color  # Reset color
        
        # Select this organism
        self.is_selected = True
        Organism.selected_organism = self
        self.entity.color = color.cyan  # Visual feedback for selection




    def _add_eyes(self) -> None:
        """Create visual eye components"""
        eye_scale = 0.35 * self.entity.scale_x
        eye_offsets = [
            Vec3(0.28, 0.25, 0.30),  # Right eye
            Vec3(-0.28, 0.25, 0.30)  # Left eye
        ]
        
        for offset in eye_offsets:
            eye = Entity(
                parent=self.entity,
                model='sphere',
                color=color.white,
                scale=eye_scale,
                position=offset,
                collider=None
            )
            Entity(
                parent=eye,
                model='sphere',
                color=color.black,
                scale=0.8 * eye_scale,
                position=Vec3(0, 0, 0.5),
                collider=None
            )
    def update(self) -> None:
        """Perform per-frame update logic"""
        if self.energy <= 0:
            self.die()
            return

        # Reset color if deselected
        if not self.is_selected and self.entity.color == color.cyan:
            self.entity.color = self.original_color

        # Behavior chain
        if not self.mating_mode:
            self._hunt_behavior()  # Ensure _hunt_behavior is called every frame
            self._check_mating_threshold()
            if not self.target_food:
                self._wander()
        else:
            self._mate_behavior()

        # Hover highlighting
        if self.entity.hovered:
            self.entity.color = Organism.HOVER_COLOR
        else:
            self.entity.color = self.original_color
        # Handle energy cost for movement
        self._handle_energy_cost()
    def _wander(self):
        """Random exploration behavior when no food is detected"""
        current_time = time.time()
        if current_time > self.next_wander_time:
            angle = random.uniform(0, 360)
            self.wander_target = Vec3(
                math.sin(math.radians(angle)),
                0,
                math.cos(math.radians(angle))
            ).normalized()
            self.next_wander_time = current_time + random.uniform(2.0, 4.0)
            self.last_position = Vec3(self.entity.position)

        if self.wander_target:
            # Calculate target rotation angle
            target_angle = math.degrees(math.atan2(-self.wander_target.x, self.wander_target.z))
            # Smooth rotation using lerp
            self.entity.rotation_y = lerp(self.entity.rotation_y, target_angle, 5 * time.dt)
            
            # Move in the forward direction (now aligned with rotation)
            move_direction = self.entity.forward.normalized()
            move_amount = move_direction * self.speed * self.wander_speed_multiplier * time.dt
            collision_ray = raycast(
                self.entity.position + Vec3(0, self.size * 0.75, 0), # Start from center height
                move_direction,
                distance=move_amount.length(),
                ignore=[self.entity],
                debug=debug,
            )
            if not collision_ray.hit:
                self.entity.position += move_amount
            # Calculate rotation using direction-to-angle conversion
            target_angle = math.degrees(math.atan2(-self.wander_target.x, self.wander_target.z))

            # Smooth rotation with quaternion slerp
            self.entity.rotation = lerp(
                self.entity.rotation,
                Vec3(0, target_angle, 0),
                5 * time.dt
            )

        # Maintain fixed height
        self.entity.y = clamp(self.entity.y, self.min_height, self.max_height)
        # Update energy costs
        self._handle_energy_cost()
    def _hunt_behavior(self):
        """Handle food-seeking behavior"""
        self._handle_energy_cost()
        self._find_food()
        # Only move to target if food exists
        if self.target_food:
            self._move_to_target()
            self._check_food_collision()
        '''def _handle_energy_cost(self) -> None:
        """Calculate and deduct movement energy costs based on distance, energy cost per meter, and metabolism."""
        distance_moved = math.dist(self.entity.position, self.last_position)
        
        # Calculate energy cost based on distance, energy cost per meter, and metabolism
        metabolism = self.genome.express_trait('metabolism')  # Ensure 'metabolism' is a trait in the genome
        
        # Total energy cost is distance moved multiplied by energy cost per meter and metabolism
        total_energy_cost = distance_moved * energy_cost_per_meter * metabolism
        
        # Deduct the energy cost
        self.energy -= int(total_energy_cost)
        
        # Update last position
        self.last_position = Vec3(self.entity.position.x, self.entity.position.y, self.entity.position.z)'''
    def _handle_energy_cost(self) -> None:
        """Calculate and deduct movement energy costs based on distance, energy cost per meter, and metabolism."""
        distance_moved = math.dist(self.entity.position, self.last_position)
        metabolism = self.genome.express_trait('metabolism')
        total_energy_cost = distance_moved * energy_cost_per_meter * metabolism
        
        #print(f"Distance moved: {distance_moved}, Metabolism: {metabolism}, Energy cost: {total_energy_cost}")
        
        self.energy -= int(total_energy_cost)
        self.last_position = Vec3(self.entity.position.x, self.entity.position.y, self.entity.position.z)
    def _vision_check(self, target_pos: Vec3) -> bool:
        """Check if target is within field of view"""
        direction_to_target = (target_pos - self.entity.position).normalized()
        # Calculate the forward vector based on the entity's rotation
        forward_vector = Vec3(
            math.sin(math.radians(self.entity.rotation_y)),
            0,
            math.cos(math.radians(self.entity.rotation_y))
        ).normalized()
        return direction_to_target.dot(forward_vector) > math.cos(self.sight_fov / 2)
    def _find_food(self) -> None:
        """Identify visible food targets using raycasting"""
        if not Food.instances:
            return

        valid_food = []
        for f in Food.instances:
            # Distance check
            dist = math.dist(self.entity.position, f.entity.position)
            if dist > self.sight_range:
                continue
                
            # FOV check
            if not self._vision_check(f.entity.position):
                continue
                '''# Raycast check for obstacles
                hit_info = raycast(
                    self.entity.position + Vec3(0, 0.8, 0),  # Adjust the ray start position
                    (f.entity.position - self.entity.position).normalized(),
                    distance=self.sight_range,
                    ignore=[self.entity],
                    debug=debug
                )'''


            # Adjust ray start position to account for food bounce
            ray_start = self.entity.position + Vec3(0, 0.1, 0)
            ray_direction = (f.entity.position - self.entity.position).normalized()
            hit_info = raycast(
                ray_start,
                ray_direction,
                distance=self.sight_range,
                ignore=[self.entity],
                debug=debug
            )
            # Debugging: Draw the ray
            '''if debug == True:
                ray_entity = Entity(
                    model='cube',
                    position=ray_start,
                    scale=(0.1, 0.1, hit_info.distance),
                    rotation=ray_direction,  # Adjust rotation to align with ray direction
                    color=color.red
                )
                destroy(ray_entity, delay=0.1)  # Remove the ray after a short delay
                '''
            if hit_info.entity == f.entity:
                valid_food.append(f)
        
        if valid_food:
            self.target_food = min(valid_food,
                key=lambda f: math.dist(self.entity.position, f.entity.position))
        else:
            self.target_food = None
    def _move_to_target(self) -> None:
        """Move towards current target with proper rotation"""
        # Check if target_food is valid and its entity exists
        if not self.target_food or not hasattr(self.target_food, 'entity') or not self.target_food.entity:
            self.target_food = None  # Reset target_food if it's invalid
            return

        # Ensure the target_food's entity has a valid position
        if not hasattr(self.target_food.entity, 'position'):
            self.target_food = None  # Reset target_food if it has no position
            return

        # Look at the target food's position
        self.entity.look_at(self.target_food.entity.position)

        # Move towards the target
        move_direction = self.entity.forward.normalized()
        move_amount = move_direction * self.speed * time.dt

        # Check for collisions
        collision_ray = raycast(
            self.entity.position + Vec3(0, self.size * 0.75, 0),  # Start from center height
            move_direction,
            distance=move_amount.length(),
            ignore=[self.entity],
            debug=debug
        )

        # Move if there's no collision
        if not collision_ray.hit:
            self.entity.position += move_amount

        # Maintain fixed height
        self.entity.y = clamp(self.entity.y, self.min_height, self.max_height)
    def _check_food_collision(self) -> None:
        if self.target_food:
            # Calculate collision distance using ACTUAL RADII (scale = diameter)
            org_radius = self.entity.scale_x / 2
            food_radius = self.target_food.entity.scale_x / 2
            collision_distance = org_radius + food_radius
            
            if math.dist(self.entity.position, self.target_food.entity.position) < collision_distance:
                self.energy += self.target_food.energy_value
                self.target_food.destroy()
                self.target_food = None

    def _check_mating_threshold(self) -> None:
        """Evaluate mating readiness"""
        mating_energy = self.default_energy * 2
        if self.energy >= mating_energy * 1.25:
            self._start_mating(probability=1.0)
        elif self.energy >= mating_energy:
            self._start_mating(probability=0.5)

    def _start_mating(self, probability: float) -> None:
        """Enter mating mode if successful"""
        if random.random() < probability:
            self.mating_mode = True
            self.entity.color = color.pink
            self.target_food = None

    def _mate_behavior(self) -> None:
        """Handle mating interactions"""
        # Look for potential mates
        candidates = [
            o for o in Organism.instances
            if o != self and o.mating_mode 
            and math.dist(o.entity.position, self.entity.position) < 2
        ]
        
        if candidates:
            self._reproduce(random.choice(candidates))
            
        # Revert if energy too low
        if self.energy < self.default_energy * 0.5:
            self._stop_mating()

    def _reproduce(self, mate: 'Organism') -> None:
        """Produce offspring with genetic recombination"""
        num_offspring = 1 if random.random() < 0.5 else 2
        cost = self.default_energy * (0.5 if num_offspring == 1 else 0.75)
        
        if self.energy < cost or mate.energy < cost:
            return
            
        self.energy -= cost
        mate.energy -= cost
        
        for _ in range(num_offspring):
            new_genome = Genome.recombine(self.genome, mate.genome)
            start_pos = lerp(self.entity.position, mate.entity.position, 0.5)
            Organism(
                position=start_pos,
                genome=new_genome,
                color=lerp(self.original_color, mate.original_color, 0.5)
            )
            
        self._stop_mating()
        mate._stop_mating()

    def _stop_mating(self) -> None:
        """Exit mating mode"""
        self.mating_mode = False
        self.entity.color = self.original_color
        self.target_food = None

    def die(self) -> None:
        """Handle organism death"""
        if self in Organism.instances:
            Organism.instances.remove(self)
        if self.entity:
            destroy(self.entity)