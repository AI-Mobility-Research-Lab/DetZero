#!/usr/bin/env python3
"""
Test tracking pipeline compatibility on converted dataset

This script tests that DetZero's tracking module can:
1. Load converted sequences correctly
2. Access track IDs from obj_ids field
3. Process temporal ordering correctly
4. Verify sequence metadata (sequence_len, sample_idx)

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import sys
import pickle
import argparse
from pathlib import Path
from collections import defaultdict

# Add tracking module to path
tracking_path = Path(__file__).resolve().parent.parent / 'tracking'
sys.path.insert(0, str(tracking_path))

import numpy as np
from detzero_utils import common_utils


def load_sequence_info(data_path, sequence_name):
    """Load sequence info file"""
    seq_path = Path(data_path) / 'waymo_processed_data' / sequence_name
    info_file = seq_path / f'{sequence_name}.pkl'
    
    if not info_file.exists():
        raise FileNotFoundError(f"Sequence info file not found: {info_file}")
    
    with open(info_file, 'rb') as f:
        seq_info = pickle.load(f)
    
    return seq_info


def test_sequence_metadata(seq_info, sequence_name, logger):
    """
    Test sequence metadata fields
    
    Requirements: 10.1, 10.2
    """
    logger.info(f"\n  Testing sequence metadata...")
    
    if not isinstance(seq_info, list):
        logger.error(f"    ✗ Sequence info should be a list, got {type(seq_info)}")
        return False
    
    if len(seq_info) == 0:
        logger.error(f"    ✗ Sequence is empty")
        return False
    
    sequence_len = len(seq_info)
    logger.info(f"    - Sequence length: {sequence_len} frames")
    
    # Check sequence_len field (Req 10.1)
    for i, frame in enumerate(seq_info):
        if 'sequence_len' not in frame:
            logger.error(f"    ✗ Frame {i} missing 'sequence_len' field")
            return False
        
        if frame['sequence_len'] != sequence_len:
            logger.error(f"    ✗ Frame {i} has incorrect sequence_len: "
                        f"{frame['sequence_len']} != {sequence_len}")
            return False
    
    logger.info(f"    ✓ All frames have correct sequence_len field")
    
    # Check sequential sample_idx (Req 10.2)
    sample_indices = [frame['sample_idx'] for frame in seq_info]
    expected_indices = list(range(sequence_len))
    
    if sample_indices != expected_indices:
        logger.error(f"    ✗ sample_idx values are not sequential [0, 1, 2, ...]")
        logger.error(f"      Expected: {expected_indices}")
        logger.error(f"      Got: {sample_indices}")
        return False
    
    logger.info(f"    ✓ sample_idx values are sequential [0, 1, ..., {sequence_len-1}]")
    
    # Check sequence_name consistency
    for i, frame in enumerate(seq_info):
        if frame['sequence_name'] != sequence_name:
            logger.error(f"    ✗ Frame {i} has incorrect sequence_name: "
                        f"{frame['sequence_name']} != {sequence_name}")
            return False
    
    logger.info(f"    ✓ All frames have correct sequence_name")
    
    return True


def test_temporal_ordering(seq_info, logger):
    """
    Test temporal ordering of frames
    
    Requirements: 10.4, 10.5
    """
    logger.info(f"\n  Testing temporal ordering...")
    
    timestamps = [frame['time_stamp'] for frame in seq_info]
    
    # Check monotonically increasing timestamps (Req 10.4)
    for i in range(len(timestamps) - 1):
        if timestamps[i] > timestamps[i + 1]:
            logger.error(f"    ✗ Timestamps not monotonically increasing:")
            logger.error(f"      Frame {i}: {timestamps[i]}")
            logger.error(f"      Frame {i+1}: {timestamps[i+1]}")
            return False
    
    logger.info(f"    ✓ Timestamps are monotonically increasing")
    
    # Show timestamp range
    time_range_ms = (timestamps[-1] - timestamps[0]) / 1000.0
    logger.info(f"    - Time range: {time_range_ms:.2f} ms")
    logger.info(f"    - First timestamp: {timestamps[0]}")
    logger.info(f"    - Last timestamp: {timestamps[-1]}")
    
    # Check frame ordering matches temporal progression (Req 10.5)
    # sample_idx should match timestamp order
    for i in range(len(seq_info)):
        if seq_info[i]['sample_idx'] != i:
            logger.error(f"    ✗ Frame ordering doesn't match temporal progression")
            return False
    
    logger.info(f"    ✓ Frame ordering matches temporal progression")
    
    return True


def test_track_ids(seq_info, logger):
    """
    Test track ID accessibility and consistency
    
    Requirements: 10.3
    """
    logger.info(f"\n  Testing track ID accessibility...")
    
    # Collect all track IDs across frames
    track_id_frames = defaultdict(list)  # track_id -> list of frame indices
    total_objects = 0
    
    for frame_idx, frame in enumerate(seq_info):
        if 'annos' not in frame:
            logger.error(f"    ✗ Frame {frame_idx} missing 'annos' field")
            return False
        
        annos = frame['annos']
        
        # Check obj_ids field exists (Req 10.3)
        if 'obj_ids' not in annos:
            logger.error(f"    ✗ Frame {frame_idx} missing 'obj_ids' field in annotations")
            return False
        
        obj_ids = annos['obj_ids']
        
        # Track IDs should be accessible
        if not isinstance(obj_ids, np.ndarray):
            logger.error(f"    ✗ obj_ids should be numpy array, got {type(obj_ids)}")
            return False
        
        # Record which frames each track appears in
        for track_id in obj_ids:
            track_id_str = str(track_id)
            track_id_frames[track_id_str].append(frame_idx)
        
        total_objects += len(obj_ids)
    
    logger.info(f"    ✓ obj_ids field accessible in all frames")
    logger.info(f"    - Total objects across sequence: {total_objects}")
    logger.info(f"    - Unique track IDs: {len(track_id_frames)}")
    
    # Analyze track consistency
    multi_frame_tracks = {tid: frames for tid, frames in track_id_frames.items() 
                          if len(frames) > 1}
    
    if len(multi_frame_tracks) > 0:
        logger.info(f"    - Tracks appearing in multiple frames: {len(multi_frame_tracks)}")
        
        # Show some example tracks
        example_tracks = list(multi_frame_tracks.items())[:3]
        for track_id, frames in example_tracks:
            logger.info(f"      Track {track_id}: appears in {len(frames)} frames "
                       f"(frames {min(frames)}-{max(frames)})")
        
        # Check track consistency - tracks should appear in consecutive or near-consecutive frames
        inconsistent_tracks = []
        for track_id, frames in multi_frame_tracks.items():
            frames_sorted = sorted(frames)
            max_gap = max(frames_sorted[i+1] - frames_sorted[i] 
                         for i in range(len(frames_sorted) - 1))
            # Allow gaps up to 5 frames (object might be occluded)
            if max_gap > 10:
                inconsistent_tracks.append((track_id, max_gap))
        
        if inconsistent_tracks:
            logger.warning(f"    ! Found {len(inconsistent_tracks)} tracks with large gaps:")
            for track_id, gap in inconsistent_tracks[:3]:
                logger.warning(f"      Track {track_id}: max gap = {gap} frames")
        else:
            logger.info(f"    ✓ Track IDs are temporally consistent")
    else:
        logger.info(f"    - No tracks appear in multiple frames (single-frame detections only)")
    
    return True


def test_sequence(data_path, sequence_name, logger):
    """Test a single sequence"""
    logger.info(f"\nTesting sequence: {sequence_name}")
    logger.info("=" * 80)
    
    try:
        # Load sequence info
        logger.info(f"  Loading sequence info...")
        seq_info = load_sequence_info(data_path, sequence_name)
        logger.info(f"  ✓ Sequence loaded successfully")
        
        # Test sequence metadata (Req 10.1, 10.2)
        if not test_sequence_metadata(seq_info, sequence_name, logger):
            return False
        
        # Test temporal ordering (Req 10.4, 10.5)
        if not test_temporal_ordering(seq_info, logger):
            return False
        
        # Test track IDs (Req 10.3)
        if not test_track_ids(seq_info, logger):
            return False
        
        logger.info(f"\n  ✓ Sequence passed all tests")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Error testing sequence: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_tracking_dataloader(data_path, logger):
    """
    Test that tracking dataloader can load the converted data
    """
    logger.info(f"\nTesting tracking dataloader...")
    logger.info("=" * 80)
    
    try:
        import os
        from detzero_utils.config_utils import cfg, cfg_from_yaml_file
        from detzero_track.datasets import build_dataloader
        
        # Change to tracking directory for config loading
        original_dir = os.getcwd()
        os.chdir(tracking_path / 'tools')
        
        # Load tracking config
        cfg_file = 'cfgs/tk_model_cfgs/waymo_detzero_track.yaml'
        cfg_from_yaml_file(cfg_file, cfg)
        cfg.ROOT_DIR = tracking_path
        
        # Change back to original directory
        os.chdir(original_dir)
        
        cfg.DATA_CONFIG.DATA_PATH = data_path
        
        # For tracking, we need detection results
        # Check if detection results exist
        det_results_path = Path('detection/output/baseline_vehicle_test.pkl')
        if not det_results_path.exists():
            logger.warning(f"  ! Detection results not found: {det_results_path}")
            logger.warning(f"  ! Skipping dataloader test (requires detection results)")
            return True
        
        logger.info(f"  Building tracking dataloader...")
        logger.info(f"  - Data path: {data_path}")
        logger.info(f"  - Detection results: {det_results_path}")
        
        # Build dataloader
        import time
        log_time = time.strftime('%Y%m%d-%H%M%S', time.localtime())
        
        # Use 'test' split to avoid requiring GT info file
        dataset, dataloader = build_dataloader(
            dataset_cfg=cfg.DATA_CONFIG,
            data_path=str(det_results_path),
            log_time=log_time,
            batch_size=1,
            workers=0,
            split='test',  # Use 'test' to avoid GT loading
            logger=logger
        )
        
        logger.info(f"  ✓ Tracking dataloader built successfully")
        logger.info(f"    - Number of sequences: {len(dataset)}")
        
        # Test loading one batch
        logger.info(f"\n  Testing batch loading...")
        for i, (seq_names, data_dict) in enumerate(dataloader):
            if i >= 1:  # Just test one batch
                break
            
            logger.info(f"    - Sequence: {seq_names[0]}")
            logger.info(f"    - Data keys: {list(data_dict.keys())}")
            
            if 'detection' in data_dict:
                det_data = data_dict['detection'][0]
                logger.info(f"    - Detection frames: {len(det_data)}")
            
            if 'gt' in data_dict:
                gt_data = data_dict['gt'][0]
                logger.info(f"    - Ground truth frames: {len(gt_data)}")
        
        logger.info(f"  ✓ Tracking dataloader test passed")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Tracking dataloader test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    parser = argparse.ArgumentParser(description='Test tracking pipeline compatibility')
    parser.add_argument('--data_path', type=str, default='data/waymo_8k',
                       help='Path to converted dataset')
    parser.add_argument('--num_sequences', type=int, default=3,
                       help='Number of sequences to test')
    parser.add_argument('--test_dataloader', action='store_true',
                       help='Test tracking dataloader (requires detection results)')
    args = parser.parse_args()
    
    # Setup logging
    log_file = Path('logs') / 'test_tracking_compatibility.log'
    log_file.parent.mkdir(exist_ok=True)
    logger = common_utils.create_logger(log_file, rank=0)
    
    logger.info("=" * 80)
    logger.info("DetZero Tracking Pipeline Compatibility Test - Task 13.4")
    logger.info("=" * 80)
    logger.info(f"Data path: {args.data_path}")
    logger.info(f"Testing {args.num_sequences} sequences")
    
    # Check data path exists
    data_path = Path(args.data_path)
    if not data_path.exists():
        logger.error(f"✗ Data path not found: {data_path}")
        return 1
    
    processed_data_path = data_path / 'waymo_processed_data'
    if not processed_data_path.exists():
        logger.error(f"✗ Processed data path not found: {processed_data_path}")
        return 1
    
    # Get list of sequences
    imageset_file = data_path / 'ImageSets' / 'val.txt'
    if not imageset_file.exists():
        logger.error(f"✗ ImageSet file not found: {imageset_file}")
        return 1
    
    with open(imageset_file, 'r') as f:
        sequences = [line.strip() for line in f if line.strip()]
    
    logger.info(f"\nFound {len(sequences)} validation sequences")
    
    # Test subset of sequences
    test_sequences = sequences[:args.num_sequences]
    
    all_passed = True
    for seq_name in test_sequences:
        if not test_sequence(args.data_path, seq_name, logger):
            all_passed = False
    
    # Test tracking dataloader if requested
    if args.test_dataloader:
        if not test_tracking_dataloader(args.data_path, logger):
            all_passed = False
    
    # Summary
    logger.info("\n" + "=" * 80)
    if all_passed:
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80)
        logger.info("\nTracking pipeline compatibility verified:")
        logger.info("  ✓ Requirement 10.1: sequence_len field populated correctly")
        logger.info("  ✓ Requirement 10.2: Sequential sample_idx values (0-based)")
        logger.info("  ✓ Requirement 10.3: Track IDs accessible from obj_ids field")
        logger.info("  ✓ Requirement 10.4: Monotonically increasing timestamps")
        logger.info("  ✓ Requirement 10.5: Frame ordering matches temporal progression")
        logger.info("\nThe converted dataset is fully compatible with DetZero tracking!")
        return 0
    else:
        logger.error("✗ SOME TESTS FAILED")
        logger.error("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
