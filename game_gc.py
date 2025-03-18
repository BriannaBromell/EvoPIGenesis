from typing import List
from ursina import Entity

class GarbageCollector:
    """System for cleaning up destroyed entities and managing memory"""
        
    @staticmethod
    def collect() -> None:
        """Remove invalid entities from all tracked lists"""
        # Import inside method to prevent circular imports
        from food import Food
        from organism import Organism
        
        # Clean food instances
        Food.instances = [f for f in Food.instances if hasattr(f, 'entity') and f.entity.enabled]
        print(f"Cleaned Food instances: {len(Food.instances)} remaining")
        
        # Clean organism instances
        Organism.instances = [o for o in Organism.instances if hasattr(o, 'entity') and o.entity.enabled]
        print(f"Cleaned Organism instances: {len(Organism.instances)} remaining")
    @staticmethod
    def full_clean() -> None:
        """Force remove all destroyed entities from all sources"""
        GarbageCollector.collect()
        
        # Clean up potential zombie entities
        for e in [e for e in Entity.entities if not e.enabled]:
            e.removeNode()
            
        # Explicit memory management
        import gc
        gc.collect()