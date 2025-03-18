
import random

from typing import Dict, Tuple
from ursina import *

class Genome:
    """Class representing a genetic blueprint for organisms"""
    __slots__ = ('alleles', 'dominance_map')
    
    def __init__(self, alleles: Dict[str, Tuple[float, float]]):
        self.alleles = alleles
        self.dominance_map = {
            'color': 0,
            'sight_fov': 0,
            'sight_range': 0,
            'strength': 0,
            'speed': 0,
            'size': 1,
            'default_energy': 0,
            'metabolism': 0
        }

    @classmethod
    def random_genome(cls) -> 'Genome':
        """Generate a random genome with paired alleles"""
        return cls({
            'color': (
                random.uniform(0, 255), 
                random.uniform(0, 255)
            ),
            'sight_fov': (
                random.uniform(115, 120), 
                random.uniform(115, 120)
            ),
            'sight_range': (
                random.uniform(8, 10), 
                random.uniform(8, 10)
            ),
            'strength': (
                random.uniform(5, 6), 
                random.uniform(5, 6)
            ),
            'speed': (
                random.uniform(1.3, 1.5), 
                random.uniform(1.3, 1.5)
            ),
            'size': (
                random.uniform(0.45, 0.55), 
                random.uniform(0.45, 0.55)
            ),
            'metabolism': (
                random.uniform(0.95, 1.05), 
                random.uniform(0.95, 1.05)
            ),
            'default_energy': (
                random.randint(500, 550), 
                random.randint(500, 550)
            )
        })

    def express_trait(self, trait: str) -> float:
        """Calculate expressed trait value based on alleles"""
        a, b = self.alleles[trait]
        dominant_idx = self.dominance_map.get(trait, 0)
        
        # Format color differently
        if trait == 'color':
            return color.hsv(a/255, b/255, 1)  # Now recognizes 'color'
            
        if dominant_idx in (0, 1):
            return (a, b)[dominant_idx]
        return (a + b) / 2
    @classmethod
    def recombine(cls, parent1: 'Genome', parent2: 'Genome') -> 'Genome':
        """Create new genome from two parents with mutation chance"""
        new_alleles = {}
        for trait in parent1.alleles:
            a = random.choice(parent1.alleles[trait])
            b = random.choice(parent2.alleles[trait])
            
            # Apply mutation (5% chance per allele)
            a *= 1 + random.uniform(-0.1, 0.1) if random.random() < 0.05 else 1
            b *= 1 + random.uniform(-0.1, 0.1) if random.random() < 0.05 else 1
            
            new_alleles[trait] = (a, b)
            
        return cls(new_alleles)