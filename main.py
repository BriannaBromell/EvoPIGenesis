#main.py
# imports
import os
import json
import time
import random
# ursina
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
#local imports
from gui import Menu, InspectionOverlay  # Import the Menu class
from organism import Organism
from food import Food
from game_gc import GarbageCollector
#--- Configuration ---
# Load config first
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)
# Set confguration variables
map_size = config['map_size']
food_spawn_rate = config['food_spawn_rate']
max_wall_height = config['max_wall_height']
#Unused, don't remove: organism_speeds = config['organisms']['food_spawn_rate']

# --- Initial declaration and setup ---
app=Ursina(
    title='EvoPiGenesis', 
    icon='assets/icon.ico', 
    borderless=True, 
    fullscreen=False, 
    size=None, 
    forced_aspect_ratio=None, 
    position=None, 
    vsync=True, 
    editor_ui_enabled=False, 
    window_type='onscreen', 
    development_mode=True)
Entity.default_shader = lit_with_shadows_shader

menu = Menu() # create the menu object.
menu_open = False # Track if the menu is open

# --- World generation and perspective ---
player=FirstPersonController()
pivot=Entity()
DirectionalLight(parent=pivot, y=2,z=3,rotation=(45, -45, 45))
Sky()
"""Create play area with walls and floor"""
for x in range(-map_size, map_size + 1):  # Generate floor from -map_size to map_size (inclusive)
    for z in range(-map_size, map_size + 1):
        # Floor tiles
        floor = Entity(
            model='cube',
            position=Vec3(x, 0, z),  # Place floor at y=0
            color=color.gray,
            texture='white_cube',
            collider='box'
        )

        # Walls at map edges
        if abs(x) == map_size or abs(z) == map_size:
            for y in range(max_wall_height):  # Walls span y=0 to y=2
                wall = Entity(
                    model='cube',
                    position=Vec3(x, y, z),  # Place walls from y=0 to y=2
                    color=color.white,
                    texture='white_cube',
                    collider='box'
                )

# --- Hud overlay (creature inspection) ---
inspection_overlay = InspectionOverlay(enabled=False)



"""Initialize starting population of organisms"""
for _ in range(10): #
    Organism(
        position=Vec3(random.uniform(-(map_size - 1), map_size - 1), 1, random.uniform(-(map_size - 1), map_size - 1)),
        color=color.hsv(random.uniform(0, 360), 0.8, 0.8)
    )
for _ in range(40):
    Food()


def input(key):
    global menu_open
    if key == 'escape':
        application.quit()
    if key == 'tab':
        menu_open = not menu_open  # Toggle the menu state
        menu.enabled = menu_open
        mouse.locked = not menu_open  # Toggle mouse lock
        mouse.visible = menu_open
        player.enabled = not menu_open  # Toggle player movement
    if key == 'left mouse down':
        if mouse.hovered_entity and isinstance(mouse.hovered_entity.parent, Organism):
            Organism.selected_organism = mouse.hovered_entity.parent
            inspection_overlay.update_info(Organism.selected_organism)  # Update overlay with organism data
            inspection_overlay.enabled = True
        else:
            if Organism.selected_organism:
                Organism.selected_organism.is_selected = False
                Organism.selected_organism = None
                inspection_overlay.enabled = False

def update():
    """Main game loop handling all real-time updates"""
    global menu_open
    
    # Update HUD text with game stats

    # Update inspection overlay
    if Organism.selected_organism:
        inspection_overlay.update_info(Organism.selected_organism)
        inspection_overlay.enabled = True
    else:
        inspection_overlay.enabled = False
    # Keep player in bounds (prevent falling)
    if player.y < -10:
        player.position = (0, 10, 0)

    # Food spawning system
    if random.random() < food_spawn_rate * time.dt:
        Food(position=(
            random.uniform(-(map_size - 1), map_size - 1),
            0.5,
            random.uniform(-(map_size - 1), map_size - 1)
        ))
    # Update all food instances
    for food in Food.instances.copy():
        food.update()
    # Update all organisms
    for org in Organism.instances.copy():
        org.update()

    # Garbage collection every 5 seconds
    if time.time() % 5 < time.dt:
        GarbageCollector.collect()


app.run()