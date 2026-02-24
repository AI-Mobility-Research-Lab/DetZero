"""Validator for verifying conversion integrity and data quality."""

import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np


class ValidationReport:
    """Container for validation results."""
    
    def __init__(self):
        self.success = True
        self.errors = []
        self.warnings = []
        self.statistics = {}
    
    def add_error(self, message: str):
        """Add error message."""
        self.errors.append(message)
        self.success = False
    
    def add_warning(self, message: str):
        """Add warning message."""
        self.warnings.append(message)
    
    def __str__(self):
        lines = []
        lines.append("=" * 60)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Status: {'PASSED' if self.success else 'FAILED'}")
        lines.append(f"Errors: {len(self.errors)}")
        lines.append(f"Warnings: {len(self.warnings)}")
        lines.append("")
        
        if self.errors:
            lines.append("ERRORS:")
            for error in self.errors:
                lines.append(f"  - {error}")
            lines.append("")
        
        if self.warnings:
            lines.append("WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")
        
        if self.statistics:
            lines.append("STATISTICS:")
            for key, value in self.statistics.items():
                lines.append(f"  {key}: {value}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class ConversionValidator:
    """Verifies conversion integrity and data quality."""
    
    def __init__(self, output_path: str):
        """Initialize validator with output directory.
        
        Args:
            output_path: Root output directory to validate
        """
        self.output_path = Path(output_path)
        self.processed_data_path = self.output_path / 'waymo_processed_data'
        self.imagesets_path = self.output_path / 'ImageSets'
        self.logger = logging.getLogger(__name__)
    
    def validate_conversion(self, expected_counts: Dict[str, int]) -> ValidationReport:
        """Validate complete conversion.
        
        Args:
            expected_counts: Dict with 'train' and 'val' frame counts
            
        Returns:
            ValidationReport with success status and detailed results
        """
        report = ValidationReport()
        
        self.logger.info("Starting validation...")
        
        # Check directory structure
        if not self.processed_data_path.exists():
            report.add_error(f"Processed data directory not found: {self.processed_data_path}")
            return report
        
        if not self.imagesets_path.exists():
            report.add_error(f"ImageSets directory not found: {self.imagesets_path}")
            return report
        
        # Validate each split
        total_frames = 0
        total_boxes = 0
        class_counts = defaultdict(int)
        
        for split, expected_count in expected_counts.items():
            imageset_file = self.imagesets_path / f'{split}.txt'
            
            if not imageset_file.exists():
                report.add_error(f"ImageSet file not found: {imageset_file}")
                continue
            
            # Load sequence names
            with open(imageset_file, 'r') as f:
                sequence_names = [line.strip() for line in f if line.strip()]
            
            self.logger.info(f"Validating {split} split: {len(sequence_names)} sequences")
            
            # Validate each sequence
            split_frames = 0
            split_boxes = 0
            
            for seq_name in sequence_names:
                seq_valid, seq_frames, seq_boxes, seq_classes = self.validate_sequence(seq_name)
                
                if not seq_valid:
                    report.add_error(f"Sequence validation failed: {seq_name}")
                
                split_frames += seq_frames
                split_boxes += seq_boxes
                
                for class_name, count in seq_classes.items():
                    class_counts[class_name] += count
            
            # Check frame count
            if split_frames != expected_count:
                report.add_error(
                    f"{split} split frame count mismatch: "
                    f"expected {expected_count}, got {split_frames}"
                )
            else:
                self.logger.info(f"{split} split: {split_frames} frames validated")
            
            total_frames += split_frames
            total_boxes += split_boxes
        
        # Compute statistics
        stats = self.compute_statistics()
        report.statistics = stats
        
        self.logger.info(f"Validation complete: {total_frames} frames, {total_boxes} boxes")
        
        return report
    
    def validate_sequence(self, sequence_name: str) -> Tuple[bool, int, int, Dict]:
        """Validate single sequence.
        
        Args:
            sequence_name: Sequence identifier
            
        Returns:
            Tuple of (is_valid, frame_count, box_count, class_distribution)
        """
        sequence_dir = self.processed_data_path / sequence_name
        info_file = sequence_dir / f'{sequence_name}.pkl'
        
        if not info_file.exists():
            self.logger.error(f"Info file not found: {info_file}")
            return False, 0, 0, {}
        
        # Load info file
        try:
            with open(info_file, 'rb') as f:
                frames = pickle.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load info file {info_file}: {e}")
            return False, 0, 0, {}
        
        if not isinstance(frames, list):
            self.logger.error(f"Invalid info file structure: expected list, got {type(frames)}")
            return False, 0, 0, {}
        
        frame_count = len(frames)
        box_count = 0
        class_counts = defaultdict(int)
        
        # Validate each frame
        for frame in frames:
            # Check required fields
            required_fields = ['sample_idx', 'sequence_name', 'sequence_len', 
                             'time_stamp', 'lidar_path', 'annos']
            for field in required_fields:
                if field not in frame:
                    self.logger.error(f"Frame missing required field: {field}")
                    return False, 0, 0, {}
            
            # Check point cloud file
            pc_path = Path(frame['lidar_path'])
            if not pc_path.exists():
                self.logger.error(f"Point cloud file not found: {pc_path}")
                return False, 0, 0, {}
            
            # Validate point cloud shape
            try:
                points = np.load(pc_path)
                if points.ndim != 2 or points.shape[1] != 4:
                    self.logger.error(
                        f"Invalid point cloud shape: expected [N, 4], got {points.shape}"
                    )
                    return False, 0, 0, {}
            except Exception as e:
                self.logger.error(f"Failed to load point cloud {pc_path}: {e}")
                return False, 0, 0, {}
            
            # Validate annotations
            annos = frame['annos']
            required_anno_fields = ['name', 'difficulty', 'dimensions', 'location',
                                   'heading_angles', 'velocity', 'obj_ids',
                                   'tracking_difficulty', 'num_points_in_gt', 'gt_boxes_lidar']
            for field in required_anno_fields:
                if field not in annos:
                    self.logger.error(f"Annotations missing required field: {field}")
                    return False, 0, 0, {}
            
            # Check gt_boxes_lidar shape
            gt_boxes = annos['gt_boxes_lidar']
            if gt_boxes.ndim != 2:
                # Handle empty case
                if len(gt_boxes) == 0:
                    # Empty is okay, reshape to [0, 9]
                    annos['gt_boxes_lidar'] = gt_boxes.reshape(0, 9)
                else:
                    self.logger.error(
                        f"Invalid gt_boxes_lidar shape: expected [N, 9], got {gt_boxes.shape}"
                    )
                    return False, 0, 0, {}
            elif len(gt_boxes) > 0 and gt_boxes.shape[1] != 9:
                self.logger.error(
                    f"Invalid gt_boxes_lidar shape: expected [N, 9], got {gt_boxes.shape}"
                )
                return False, 0, 0, {}
            
            # Count boxes and classes
            n_boxes = len(annos['name'])
            box_count += n_boxes
            
            for class_name in annos['name']:
                class_counts[class_name] += 1
        
        return True, frame_count, box_count, dict(class_counts)
    
    def compute_statistics(self) -> Dict:
        """Compute dataset statistics.
        
        Returns:
            Dict with statistics
        """
        stats = {
            'total_frames': 0,
            'total_boxes': 0,
            'total_sequences': 0,
            'boxes_per_frame': 0.0,
            'class_distribution': {},
            'sequence_lengths': {},
        }
        
        if not self.processed_data_path.exists():
            return stats
        
        class_counts = defaultdict(int)
        total_boxes = 0
        total_frames = 0
        
        # Iterate through all sequences
        for seq_dir in self.processed_data_path.iterdir():
            if not seq_dir.is_dir():
                continue
            
            seq_name = seq_dir.name
            info_file = seq_dir / f'{seq_name}.pkl'
            
            if not info_file.exists():
                continue
            
            try:
                with open(info_file, 'rb') as f:
                    frames = pickle.load(f)
                
                seq_len = len(frames)
                stats['sequence_lengths'][seq_name] = seq_len
                total_frames += seq_len
                
                for frame in frames:
                    annos = frame.get('annos', {})
                    names = annos.get('name', np.array([]))
                    total_boxes += len(names)
                    
                    for class_name in names:
                        class_counts[class_name] += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to process sequence {seq_name}: {e}")
        
        stats['total_frames'] = total_frames
        stats['total_boxes'] = total_boxes
        stats['total_sequences'] = len(stats['sequence_lengths'])
        stats['boxes_per_frame'] = total_boxes / total_frames if total_frames > 0 else 0.0
        stats['class_distribution'] = dict(class_counts)
        
        return stats
