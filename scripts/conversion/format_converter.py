"""Format converter for transforming nuScenes data to DetZero Waymo format."""

import logging
from pathlib import Path
from typing import Dict, List
import numpy as np

from class_mapper import ClassMapper


class FormatConverter:
    """Transforms nuScenes data to DetZero Waymo format."""
    
    def __init__(self, class_mapper: ClassMapper, output_path: str):
        """Initialize converter with class mapper and output directory.
        
        Args:
            class_mapper: ClassMapper instance for class translation
            output_path: Root output directory for converted data
        """
        self.class_mapper = class_mapper
        self.output_path = Path(output_path)
        self.logger = logging.getLogger(__name__)
        
        # Statistics tracking
        self.stats = {
            'frames_converted': 0,
            'boxes_converted': 0,
            'frames_skipped': 0,
        }
    
    def convert_sequence(self, frames: List[Dict], sequence_name: str) -> List[Dict]:
        """Convert a sequence of frames to DetZero format.
        
        Args:
            frames: List of nuScenes frame info dicts (chronologically ordered)
            sequence_name: Unique sequence identifier
            
        Returns:
            List of converted frame dicts in DetZero format
        """
        sequence_len = len(frames)
        converted_frames = []
        
        for sample_idx, frame in enumerate(frames):
            try:
                converted_frame = self.convert_frame(
                    frame, sample_idx, sequence_name, sequence_len
                )
                converted_frames.append(converted_frame)
                self.stats['frames_converted'] += 1
            except Exception as e:
                self.logger.error(
                    f"Failed to convert frame {frame.get('token', 'unknown')} "
                    f"in sequence {sequence_name}: {e}"
                )
                self.stats['frames_skipped'] += 1
        
        return converted_frames
    
    def convert_frame(self, frame: Dict, sample_idx: int, 
                     sequence_name: str, sequence_len: int) -> Dict:
        """Convert single frame to DetZero format.
        
        Args:
            frame: nuScenes frame info dict
            sample_idx: Frame index within sequence (0-based)
            sequence_name: Sequence identifier
            sequence_len: Total frames in sequence
            
        Returns:
            Frame info dict with DetZero structure
        """
        # Convert annotations
        annos = self.convert_annotations(frame)
        
        # Build DetZero frame info
        converted = {
            'sample_idx': sample_idx,
            'sequence_name': sequence_name,
            'sequence_len': sequence_len,
            'time_stamp': int(frame.get('timestamp', 0)),
            'lidar_path': '',  # Will be set by FileWriter
            'annos': annos,
        }
        
        return converted
    
    def convert_annotations(self, frame: Dict) -> Dict:
        """Convert annotations to DetZero format.
        
        Args:
            frame: nuScenes frame info dict
            
        Returns:
            Annotation dict with DetZero structure
        """
        # Extract nuScenes annotations
        gt_boxes = frame.get('gt_boxes', np.zeros((0, 9), dtype=np.float32))
        gt_names = frame.get('gt_names', np.array([]))
        gt_boxes_velocity = frame.get('gt_boxes_velocity', np.zeros((len(gt_names), 3), dtype=np.float32))
        num_lidar_pts = frame.get('num_lidar_pts', np.zeros(len(gt_names), dtype=np.int32))
        gt_track_ids = frame.get('gt_track_ids', np.arange(len(gt_names), dtype=np.int32))
        
        # Extract vx, vy from velocity (ignore vz if present)
        if gt_boxes_velocity.shape[1] >= 2:
            gt_velocity = gt_boxes_velocity[:, :2]
        else:
            gt_velocity = np.zeros((len(gt_names), 2), dtype=np.float32)
        
        # Convert track IDs to strings
        track_id_strings = np.array([f'track_{tid}' for tid in gt_track_ids])
        
        # Ensure arrays have correct shape
        n_objects = len(gt_names)
        
        if len(gt_boxes) != n_objects:
            self.logger.warning(f"Box count mismatch: {len(gt_boxes)} boxes, {n_objects} names")
            # Truncate or pad to match
            if len(gt_boxes) > n_objects:
                gt_boxes = gt_boxes[:n_objects]
            else:
                # Pad with zeros
                padding = np.zeros((n_objects - len(gt_boxes), 9), dtype=np.float32)
                gt_boxes = np.vstack([gt_boxes, padding]) if len(gt_boxes) > 0 else padding
        
        # Handle missing velocity
        if len(gt_velocity) != n_objects:
            gt_velocity = np.zeros((n_objects, 2), dtype=np.float32)
        
        # Build annotation dict before filtering
        raw_annos = {
            'name': gt_names,
            'gt_boxes_lidar': gt_boxes,
            'velocity': gt_velocity,
            'num_points_in_gt': num_lidar_pts,
            'obj_ids': track_id_strings,
        }
        
        # Filter unmapped classes
        filtered_annos = self.class_mapper.filter_annotations(gt_names, raw_annos)
        
        # Extract filtered data
        n_filtered = len(filtered_annos['name'])
        
        # Build final DetZero annotation structure
        annos = {
            'name': filtered_annos['name'],
            'difficulty': np.zeros(n_filtered, dtype=np.int32),  # Unknown difficulty
            'dimensions': filtered_annos['gt_boxes_lidar'][:, 3:6] if n_filtered > 0 else np.zeros((0, 3), dtype=np.float32),  # [l, w, h]
            'location': filtered_annos['gt_boxes_lidar'][:, :3] if n_filtered > 0 else np.zeros((0, 3), dtype=np.float32),  # [x, y, z]
            'heading_angles': filtered_annos['gt_boxes_lidar'][:, 6] if n_filtered > 0 else np.zeros(0, dtype=np.float32),  # heading
            'velocity': filtered_annos['velocity'] if n_filtered > 0 else np.zeros((0, 2), dtype=np.float32),
            'obj_ids': filtered_annos['obj_ids'],
            'tracking_difficulty': np.zeros(n_filtered, dtype=np.int32),  # Unknown tracking difficulty
            'num_points_in_gt': filtered_annos['num_points_in_gt'] if n_filtered > 0 else np.zeros(0, dtype=np.int32),
            'gt_boxes_lidar': filtered_annos['gt_boxes_lidar'] if n_filtered > 0 else np.zeros((0, 9), dtype=np.float32),  # Full [N, 9] format
        }
        
        self.stats['boxes_converted'] += n_filtered
        
        return annos
    
    def convert_point_cloud(self, src_path: str, dst_path: str):
        """Convert point cloud to .npy format with shape [N, 4].
        
        Handles both 4-channel (x, y, z, intensity) and 5-channel 
        (x, y, z, intensity, timestamp) formats.
        
        Args:
            src_path: Source point cloud path (.bin file)
            dst_path: Destination path (.npy file)
        """
        src_path = Path(src_path)
        dst_path = Path(dst_path)
        
        if not src_path.exists():
            raise FileNotFoundError(f"Source point cloud not found: {src_path}")
        
        # Load point cloud
        points = np.fromfile(str(src_path), dtype=np.float32)
        
        # Determine number of channels
        if len(points) % 5 == 0:
            # 5-channel format: x, y, z, intensity, timestamp
            points = points.reshape(-1, 5)
            points_4d = points[:, :4]  # Drop timestamp
        elif len(points) % 4 == 0:
            # 4-channel format: x, y, z, intensity (already correct)
            points_4d = points.reshape(-1, 4)
        else:
            raise ValueError(
                f"Invalid point cloud format: {len(points)} values "
                f"(not divisible by 4 or 5)"
            )
        
        # Save as .npy
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(dst_path, points_4d)
    
    def get_statistics(self) -> Dict:
        """Get conversion statistics.
        
        Returns:
            Dict with conversion stats
        """
        return self.stats.copy()
