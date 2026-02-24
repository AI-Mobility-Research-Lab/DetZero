"""Data reader for loading nuScenes dataset from OpenPCDet format."""

import pickle
from pathlib import Path
from typing import Dict, List
import numpy as np
import logging


class NuScenesDataReader:
    """Reader for nuScenes data in OpenPCDet format."""
    
    def __init__(self, data_path: str, version: str):
        """Initialize reader with dataset path and version.
        
        Args:
            data_path: Path to OpenPCDet nuScenes data directory
            version: Dataset version (e.g., 'v1.0-tak_8k_human_combined')
        """
        self.data_path = Path(data_path)
        self.version = version
        self.logger = logging.getLogger(__name__)
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path not found: {self.data_path}")
        
        self.logger.info(f"Initialized NuScenesDataReader: {self.data_path} / {self.version}")
    
    def load_info_file(self, split: str) -> List[Dict]:
        """Load info pickle file for train or val split.
        
        Args:
            split: Dataset split ('train' or 'val')
            
        Returns:
            List of frame info dictionaries with keys:
            - lidar_path: Path to point cloud file
            - token: Unique frame identifier
            - timestamp: Frame timestamp
            - sweeps: List of sweep metadata
            - gt_boxes: Ground truth boxes [N, 9]
            - gt_names: Object class names [N]
            - gt_boxes_velocity: Object velocities [N, 2 or 3]
            - num_lidar_pts: Points in each box [N]
            - gt_track_ids: Track IDs [N]
        """
        info_file = self.data_path / self.version / f'nuscenes_infos_1sweeps_{split}.pkl'
        
        if not info_file.exists():
            raise FileNotFoundError(
                f"Info file not found: {info_file}\n"
                f"Expected format: {self.data_path}/{self.version}/nuscenes_infos_1sweeps_{{split}}.pkl"
            )
        
        self.logger.info(f"Loading info file: {info_file}")
        
        try:
            with open(info_file, 'rb') as f:
                infos = pickle.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load info file {info_file}: {e}")
        
        # Validate info structure
        if not isinstance(infos, list) or len(infos) == 0:
            raise ValueError(f"Invalid info file structure: expected non-empty list, got {type(infos)}")
        
        self.logger.info(f"Loaded {len(infos)} frames from {split} split")
        
        return infos
    
    def load_point_cloud(self, lidar_path: str) -> np.ndarray:
        """Load point cloud from file.
        
        Args:
            lidar_path: Path to point cloud file (.bin format)
            
        Returns:
            Point cloud array with shape [N, 5] (x, y, z, intensity, timestamp)
        """
        lidar_path = Path(lidar_path)
        
        if not lidar_path.exists():
            raise FileNotFoundError(f"Point cloud file not found: {lidar_path}")
        
        try:
            # nuScenes point clouds are stored as .bin files with 5 channels
            points = np.fromfile(str(lidar_path), dtype=np.float32).reshape(-1, 5)
        except Exception as e:
            raise RuntimeError(f"Failed to load point cloud {lidar_path}: {e}")
        
        return points
