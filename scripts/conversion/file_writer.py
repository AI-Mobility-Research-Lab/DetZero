"""File writer for saving converted data in DetZero format."""

import pickle
import logging
from pathlib import Path
from typing import Dict, List
import yaml


class FileWriter:
    """Writes converted data to disk in DetZero format."""
    
    def __init__(self, output_path: str):
        """Initialize writer with output directory.
        
        Args:
            output_path: Root output directory
        """
        self.output_path = Path(output_path)
        self.processed_data_path = self.output_path / 'waymo_processed_data'
        self.imagesets_path = self.output_path / 'ImageSets'
        self.logger = logging.getLogger(__name__)
        
        # Create directory structure
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        self.imagesets_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Initialized FileWriter: {self.output_path}")
    
    def write_sequence(self, sequence_name: str, frames: List[Dict], 
                      source_data_path: Path):
        """Write sequence info file and point clouds.
        
        Creates directory structure:
        {output_path}/waymo_processed_data/{sequence_name}/
            - {sequence_name}.pkl (info file)
            - 0000.npy, 0001.npy, ... (point clouds)
        
        Args:
            sequence_name: Sequence identifier
            frames: List of converted frame dicts
            source_data_path: Path to source nuScenes data for point clouds
        """
        sequence_dir = self.processed_data_path / sequence_name
        sequence_dir.mkdir(parents=True, exist_ok=True)
        
        # Update lidar_path in frames and copy point clouds
        for frame in frames:
            sample_idx = frame['sample_idx']
            pc_filename = f'{sample_idx:04d}.npy'
            pc_path = sequence_dir / pc_filename
            
            # Update lidar_path to absolute path
            frame['lidar_path'] = str(pc_path.absolute())
        
        # Write sequence info pickle file
        info_file = sequence_dir / f'{sequence_name}.pkl'
        try:
            with open(info_file, 'wb') as f:
                pickle.dump(frames, f, protocol=4)
            self.logger.debug(f"Wrote sequence info: {info_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to write sequence info {info_file}: {e}")
    
    def write_point_cloud(self, npy_array, dst_path: Path):
        """Write point cloud numpy array to file.
        
        Args:
            npy_array: Point cloud array [N, 4]
            dst_path: Destination .npy file path
        """
        import numpy as np
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(dst_path, npy_array)
    
    def write_imageset(self, sequence_names: List[str], split: str):
        """Write ImageSets/{split}.txt with sequence names.
        
        Args:
            sequence_names: List of sequence names
            split: Dataset split ('train' or 'val')
        """
        imageset_file = self.imagesets_path / f'{split}.txt'
        
        try:
            with open(imageset_file, 'w') as f:
                for seq_name in sequence_names:
                    f.write(f'{seq_name}\n')
            self.logger.info(f"Wrote ImageSet file: {imageset_file} ({len(sequence_names)} sequences)")
        except Exception as e:
            raise RuntimeError(f"Failed to write ImageSet file {imageset_file}: {e}")
    
    def write_config(self, config: Dict):
        """Write dataset configuration YAML file.
        
        Args:
            config: Configuration dict
        """
        config_file = self.output_path / 'nuscenes_8k_detzero.yaml'
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Wrote config file: {config_file}")
        except Exception as e:
            raise RuntimeError(f"Failed to write config file {config_file}: {e}")
