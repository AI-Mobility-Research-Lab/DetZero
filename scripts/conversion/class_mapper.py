"""Class mapper for converting nuScenes classes to Waymo taxonomy."""

import logging
from typing import Dict, Optional
import numpy as np


class ClassMapper:
    """Maps nuScenes object classes to Waymo class taxonomy."""
    
    # Class mapping table: nuScenes -> Waymo
    NUSCENES_TO_WAYMO = {
        'car': 'Vehicle',
        'truck': 'Vehicle',
        'bus': 'Vehicle',
        'trailer': 'Vehicle',
        'construction_vehicle': 'Vehicle',
        'pedestrian': 'Pedestrian',
        'bicycle': 'Cyclist',
        'motorcycle': 'Cyclist',
    }
    
    def __init__(self):
        """Initialize class mapper."""
        self.logger = logging.getLogger(__name__)
        self.unmapped_counts = {}  # Track unmapped class counts for logging
    
    def map_class(self, nuscenes_class: str) -> Optional[str]:
        """Map nuScenes class to Waymo class.
        
        Args:
            nuscenes_class: nuScenes class name
            
        Returns:
            Waymo class name or None if no mapping exists
        """
        waymo_class = self.NUSCENES_TO_WAYMO.get(nuscenes_class)
        
        if waymo_class is None:
            # Track unmapped classes
            self.unmapped_counts[nuscenes_class] = self.unmapped_counts.get(nuscenes_class, 0) + 1
        
        return waymo_class
    
    def filter_annotations(self, names: np.ndarray, annotations: Dict) -> Dict:
        """Filter annotations to only include mapped classes.
        
        Removes objects with unmapped classes and logs warnings.
        
        Args:
            names: Array of class names [N]
            annotations: Dict with annotation arrays (all with length N)
            
        Returns:
            Filtered annotation dict with only mapped classes
        """
        # Find indices of mapped classes
        mapped_mask = np.array([self.map_class(name) is not None for name in names])
        
        if not np.any(mapped_mask):
            # No mapped classes, return empty annotations
            return {key: np.array([]) for key in annotations.keys()}
        
        # Filter all annotation arrays
        filtered = {}
        for key, value in annotations.items():
            if isinstance(value, np.ndarray) and len(value) == len(names):
                filtered[key] = value[mapped_mask]
            else:
                filtered[key] = value
        
        # Map class names
        if 'name' in filtered:
            filtered['name'] = np.array([self.map_class(name) for name in filtered['name']])
        
        return filtered
    
    def log_unmapped_summary(self):
        """Log summary of unmapped classes encountered."""
        if self.unmapped_counts:
            self.logger.warning(f"Encountered {len(self.unmapped_counts)} unmapped class types:")
            for class_name, count in sorted(self.unmapped_counts.items(), key=lambda x: -x[1]):
                self.logger.warning(f"  {class_name}: {count} objects")
        else:
            self.logger.info("All classes successfully mapped")
