from ursina import *
from ursina.prefabs.button import Button
class InspectionOverlay(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,  # Attach to the UI camera
            position=(-0.8, 0.45),  # Top-left corner of the screen
            scale=(0.4, 0.6),  # Scale of the panel
            **kwargs
        )
        self.current_organism = None  # Initialize organism reference

        # Background panel
        self.background = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 0.8),  # Semi-transparent black
            scale=(1, 1),  # Ensure the panel is large enough
            origin=(-0.5, 0.5),  # Top-left alignment
            texture='white_cube'  # Add a texture for debugging
        )

        # Text display
        self.text = Text(
            parent=self.background,
            text="No organism selected",
            origin=(-0.5, 0.5),  # Top-left alignment
            position=(0.15, -0.15),  # Padding
            scale=(2, 2),  # Adjusted text size
            color=color.white,  # White text
            wordwrap=15  # Wrap text after 10 characters
        )

    def update_info(self, organism=None):
        """Update with organism data"""
        if organism:
            self.current_organism = organism  # Update organism reference
        
        if not self.current_organism:
            self.text.text = "No organism selected"
            return
            
        genome_info = "\n".join([f"{trait}: {round(self.current_organism.genome.express_trait(trait), 2)}" 
                               for trait in self.current_organism.genome.alleles])
        
        state_info = f"""
    Energy: {self.current_organism.energy}
    Mode: {'MATING' if self.current_organism.mating_mode else 'HUNTING'}
    Target: {'Food' if self.current_organism.target_food else 'None'}
    Position: {tuple(round(v, 1) for v in self.current_organism.entity.position)}
        """.strip()
        
        full_text = f"=== ORGANISM STATS ===\n{state_info}\n\n=== GENOME TRAITS ===\n{genome_info}"
        self.text.text = full_text  # Update the text cleanly

    def toggle(self):
        self.enabled = not self.enabled

class Menu(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent=camera.ui,  # Attach to the UI camera
            position=(0, 0),  # Center of the screen
            scale=(0.4, 0.5),  # Scale of the menu
            enabled=False,  # Disabled by default
            **kwargs
        )

        # Background panel
        self.background = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0.2, 0.2, 0.2, 0.9),  # Semi-transparent dark gray
            scale=(1, 1),
            origin=(0, 0)  # Center alignment
        )

        # Buttons
        self.resume_button = Button(
            parent=self.background,
            text="Resume",
            position=(0, 0.2),
            scale=(0.3, 0.1),
            color=color.blue,
            on_click=self.toggle
        )

        self.exit_button = Button(
            parent=self.background,
            text="Exit",
            position=(0, -0.2),
            scale=(0.3, 0.1),
            color=color.red,
            on_click=application.quit
        )

    def toggle(self):
        self.enabled = not self.enabled
        mouse.locked = not self.enabled  # Toggle mouse lock
        mouse.visible = self.enabled  # Toggle mouse visibility