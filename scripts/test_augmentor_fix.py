#!/usr/bin/env python3
"""Test that augmentor functions handle empty gt_boxes correctly"""

import sys
sys.path.insert(0, 'detection')

import numpy as np
from detzero_det.datasets.augmentor import augmentor_utils

def test_empty_gt_boxes():
    """Test all augmentor functions with empty gt_boxes"""
    
    # Create empty gt_boxes with correct shape [0, 9]
    gt_boxes_empty = np.array([]).reshape(0, 9)
    points = np.random.randn(1000, 4)
    
    print("Testing augmentor functions with empty gt_boxes...")
    
    # Test random_flip_along_x
    try:
        gt_boxes_out, points_out = augmentor_utils.random_flip_along_x(gt_boxes_empty.copy(), points.copy())
        print("✅ random_flip_along_x: PASSED")
    except Exception as e:
        print(f"❌ random_flip_along_x: FAILED - {e}")
        return False
    
    # Test random_flip_along_y
    try:
        gt_boxes_out, points_out = augmentor_utils.random_flip_along_y(gt_boxes_empty.copy(), points.copy())
        print("✅ random_flip_along_y: PASSED")
    except Exception as e:
        print(f"❌ random_flip_along_y: FAILED - {e}")
        return False
    
    # Test global_rotation
    try:
        gt_boxes_out, points_out = augmentor_utils.global_rotation(gt_boxes_empty.copy(), points.copy(), [-0.78539816, 0.78539816])
        print("✅ global_rotation: PASSED")
    except Exception as e:
        print(f"❌ global_rotation: FAILED - {e}")
        return False
    
    # Test global_scaling
    try:
        gt_boxes_out, points_out = augmentor_utils.global_scaling(gt_boxes_empty.copy(), points.copy(), [0.95, 1.05])
        print("✅ global_scaling: PASSED")
    except Exception as e:
        print(f"❌ global_scaling: FAILED - {e}")
        return False
    
    # Test global_translation
    try:
        gt_boxes_out, points_out = augmentor_utils.global_translation(gt_boxes_empty.copy(), points.copy(), 0.5)
        print("✅ global_translation: PASSED")
    except Exception as e:
        print(f"❌ global_translation: FAILED - {e}")
        return False
    
    print("\n✅ All augmentor functions handle empty gt_boxes correctly!")
    return True

if __name__ == '__main__':
    success = test_empty_gt_boxes()
    exit(0 if success else 1)
