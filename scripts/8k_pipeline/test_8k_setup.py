#!/usr/bin/env python3
"""Test script to verify 8K pipeline setup before running."""

import sys
from pathlib import Path
import pickle

def check_file(path, description):
    """Check if a file exists."""
    p = Path(path)
    if p.exists():
        size = p.stat().st_size / (1024**2)  # MB
        print(f"✅ {description}")
        print(f"   Path: {path}")
        print(f"   Size: {size:.1f} MB")
        return True
    else:
        print(f"❌ {description}")
        print(f"   Path: {path}")
        print(f"   ERROR: File not found!")
        return False

def check_dataset(path, description):
    """Check if dataset exists and is valid."""
    p = Path(path)
    if not p.exists():
        print(f"❌ {description}")
        print(f"   Path: {path}")
        print(f"   ERROR: Directory not found!")
        return False
    
    # Check for info files
    train_info = p / 'nuscenes_infos_1sweeps_train.pkl'
    val_info = p / 'nuscenes_infos_1sweeps_val.pkl'
    
    if not train_info.exists() or not val_info.exists():
        print(f"❌ {description}")
        print(f"   Path: {path}")
        print(f"   ERROR: Info files not found!")
        return False
    
    # Load and check
    try:
        with open(train_info, 'rb') as f:
            train_data = pickle.load(f)
        with open(val_info, 'rb') as f:
            val_data = pickle.load(f)
        
        print(f"✅ {description}")
        print(f"   Path: {path}")
        print(f"   Train samples: {len(train_data)}")
        print(f"   Val samples: {len(val_data)}")
        return True
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Path: {path}")
        print(f"   ERROR: {e}")
        return False

def main():
    print("=" * 80)
    print("DetZero 8K Pipeline Setup Verification")
    print("=" * 80)
    print()
    
    checks = []
    
    # Check 1: Dataset
    print("1. Checking 8K nuScenes Dataset...")
    checks.append(check_dataset(
        '/home/aimob/projects/OpenPCDet/data/nuscenes_custom/v1.0-tak_8k_human_combined',
        '8K nuScenes Dataset'
    ))
    print()
    
    # Check 2: Pre-trained model
    print("2. Checking Pre-trained Model...")
    checks.append(check_file(
        'detection/output/centerpoint_8k/checkpoint_epoch_80.pth',
        'CenterPoint 8K Model (80 epochs)'
    ))
    print()
    
    # Check 3: Detection config
    print("3. Checking Detection Config...")
    checks.append(check_file(
        'detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml',
        'Detection Model Config'
    ))
    checks.append(check_file(
        'detection/tools/cfgs/det_dataset_cfgs/nuscenes_custom_8k.yaml',
        'Detection Dataset Config'
    ))
    print()
    
    # Check 4: Tracking config
    print("4. Checking Tracking Config...")
    checks.append(check_file(
        'tracking/tools/cfgs/tk_model_cfgs/detzero_track_8k.yaml',
        'Tracking Model Config'
    ))
    checks.append(check_file(
        'tracking/tools/cfgs/tk_dataset_cfgs/nuscenes_custom_8k_dataset.yaml',
        'Tracking Dataset Config'
    ))
    print()
    
    # Check 5: Scripts
    print("5. Checking Pipeline Scripts...")
    checks.append(check_file(
        'run_detection_8k.py',
        'Detection Script'
    ))
    checks.append(check_file(
        'run_8k_pipeline.sh',
        'Full Pipeline Script'
    ))
    print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print()
        print("You're ready to run the pipeline!")
        print()
        print("Quick start:")
        print("  ./run_8k_pipeline.sh")
        print()
        print("Or run detection only:")
        print("  python3 run_detection_8k.py")
        print()
        return 0
    else:
        print(f"❌ Some checks failed ({passed}/{total} passed)")
        print()
        print("Please fix the issues above before running the pipeline.")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
