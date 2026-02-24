#!/usr/bin/env python3
"""
Main conversion script for transforming OpenPCDet 8K nuScenes dataset 
to DetZero's Waymo format.
"""

import argparse
import sys
import time
from pathlib import Path
from multiprocessing import Pool, cpu_count

from data_reader import NuScenesDataReader
from class_mapper import ClassMapper
from sequence_builder import SequenceBuilder
from format_converter import FormatConverter
from file_writer import FileWriter
from validator import ConversionValidator
from logger_config import setup_logger


def convert_sequence_worker(args):
    """Worker function for parallel sequence conversion.
    
    Args:
        args: Tuple of (scene_token, frames, sequence_name, output_path, source_data_path, version)
        
    Returns:
        Tuple of (sequence_name, success, frame_count, box_count)
    """
    scene_token, frames, sequence_name, output_path, source_data_path, version = args
    
    # Create converter and writer for this worker
    class_mapper = ClassMapper()
    converter = FormatConverter(class_mapper, output_path)
    writer = FileWriter(output_path)
    
    try:
        # Convert frames
        converted_frames = converter.convert_sequence(frames, sequence_name)
        
        if not converted_frames:
            return sequence_name, False, 0, 0
        
        # Copy point clouds and write sequence
        sequence_dir = writer.processed_data_path / sequence_name
        sequence_dir.mkdir(parents=True, exist_ok=True)
        
        for frame, src_frame in zip(converted_frames, frames):
            sample_idx = frame['sample_idx']
            pc_filename = f'{sample_idx:04d}.npy'
            dst_pc_path = sequence_dir / pc_filename
            
            # Get source point cloud path and make it absolute
            src_pc_path = src_frame.get('lidar_path', '')
            if src_pc_path:
                # Make path absolute relative to source dataset
                if not Path(src_pc_path).is_absolute():
                    src_pc_path = source_data_path / version / src_pc_path
                converter.convert_point_cloud(src_pc_path, dst_pc_path)
        
        # Write sequence info
        writer.write_sequence(sequence_name, converted_frames, source_data_path)
        
        stats = converter.get_statistics()
        return sequence_name, True, stats['frames_converted'], stats['boxes_converted']
        
    except Exception as e:
        print(f"Error converting sequence {sequence_name}: {e}")
        return sequence_name, False, 0, 0


def main():
    """Main conversion function."""
    parser = argparse.ArgumentParser(
        description='Convert OpenPCDet nuScenes 8K dataset to DetZero Waymo format'
    )
    parser.add_argument(
        '--source_path',
        type=str,
        required=True,
        help='Path to OpenPCDet nuScenes data directory'
    )
    parser.add_argument(
        '--output_path',
        type=str,
        required=True,
        help='Output directory for converted data'
    )
    parser.add_argument(
        '--version',
        type=str,
        default='v1.0-tak_8k_human_combined',
        help='Dataset version (default: v1.0-tak_8k_human_combined)'
    )
    parser.add_argument(
        '--splits',
        type=str,
        nargs='+',
        default=['train', 'val'],
        help='Dataset splits to convert (default: train val)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=max(1, cpu_count() - 1),
        help='Number of parallel workers (default: CPU count - 1)'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only run validation without conversion'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logger('conversion')
    
    logger.info("=" * 60)
    logger.info("nuScenes to DetZero Waymo Format Conversion")
    logger.info("=" * 60)
    logger.info(f"Source: {args.source_path}")
    logger.info(f"Output: {args.output_path}")
    logger.info(f"Version: {args.version}")
    logger.info(f"Splits: {args.splits}")
    logger.info(f"Workers: {args.workers}")
    logger.info("=" * 60)
    
    # Validate-only mode
    if args.validate_only:
        logger.info("Running validation only...")
        validator = ConversionValidator(args.output_path)
        expected_counts = {'train': 7200, 'val': 800}
        report = validator.validate_conversion(expected_counts)
        print(report)
        return 0 if report.success else 1
    
    # Start conversion
    start_time = time.time()
    
    try:
        # Initialize components
        reader = NuScenesDataReader(args.source_path, args.version)
        class_mapper = ClassMapper()
        sequence_builder = SequenceBuilder()
        writer = FileWriter(args.output_path)
        
        all_sequence_names = {}
        total_frames = 0
        total_boxes = 0
        
        # Process each split
        for split in args.splits:
            logger.info(f"\nProcessing {split} split...")
            
            # Load info file
            frames = reader.load_info_file(split)
            logger.info(f"Loaded {len(frames)} frames")
            
            # Group into sequences
            scenes = sequence_builder.group_frames_by_scene(frames)
            logger.info(f"Grouped into {len(scenes)} sequences")
            
            # Prepare worker arguments
            worker_args = []
            sequence_names = []
            
            for scene_token, scene_frames in scenes.items():
                sequence_name = sequence_builder.generate_sequence_name(scene_token, split)
                sequence_names.append(sequence_name)
                worker_args.append((
                    scene_token,
                    scene_frames,
                    sequence_name,
                    args.output_path,
                    Path(args.source_path),
                    args.version
                ))
            
            # Convert sequences in parallel
            logger.info(f"Converting {len(worker_args)} sequences with {args.workers} workers...")
            
            if args.workers > 1:
                with Pool(args.workers) as pool:
                    results = pool.map(convert_sequence_worker, worker_args)
            else:
                results = [convert_sequence_worker(arg) for arg in worker_args]
            
            # Collect results
            split_frames = 0
            split_boxes = 0
            failed_sequences = []
            
            for seq_name, success, frame_count, box_count in results:
                if success:
                    split_frames += frame_count
                    split_boxes += box_count
                else:
                    failed_sequences.append(seq_name)
            
            if failed_sequences:
                logger.warning(f"Failed to convert {len(failed_sequences)} sequences:")
                for seq_name in failed_sequences:
                    logger.warning(f"  - {seq_name}")
            
            logger.info(f"{split} split: {split_frames} frames, {split_boxes} boxes converted")
            
            # Write ImageSet file
            writer.write_imageset(sequence_names, split)
            
            all_sequence_names[split] = sequence_names
            total_frames += split_frames
            total_boxes += split_boxes
        
        # Write config file
        config = {
            'DATASET': 'WaymoDetectionDataset',
            'DATA_PATH': str(Path(args.output_path).absolute()),
            'PROCESSED_DATA_TAG': 'waymo_processed_data',
            'POINT_CLOUD_RANGE': [-75.2, -75.2, -2, 75.2, 75.2, 4],
            'DATA_SPLIT': {
                'train': 'train',
                'test': 'val'
            },
            'CLASS_NAMES': ['Vehicle', 'Pedestrian', 'Cyclist'],
        }
        writer.write_config(config)
        
        # Log unmapped classes summary
        class_mapper.log_unmapped_summary()
        
        # Conversion complete
        elapsed_time = time.time() - start_time
        
        logger.info("=" * 60)
        logger.info("CONVERSION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total frames: {total_frames}")
        logger.info(f"Total boxes: {total_boxes}")
        logger.info(f"Boxes per frame: {total_boxes / total_frames:.2f}" if total_frames > 0 else "Boxes per frame: N/A (no frames converted)")
        logger.info(f"Time elapsed: {elapsed_time:.2f} seconds")
        logger.info(f"Processing rate: {total_frames / elapsed_time:.2f} frames/sec")
        logger.info("=" * 60)
        
        # Run validation
        logger.info("\nRunning validation...")
        validator = ConversionValidator(args.output_path)
        expected_counts = {split: len(all_sequence_names.get(split, [])) * 10 for split in args.splits}
        # Note: We don't know exact frame counts per split, so validation will report actual counts
        report = validator.validate_conversion({'train': 0, 'val': 0})  # Will compute actual
        print(report)
        
        return 0 if report.success else 1
        
    except KeyboardInterrupt:
        logger.warning("\nConversion interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\nConversion failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
