#!/usr/bin/env python3
"""
Convert DetZero pickle results to JSON for web visualization
"""

import pickle
import json
import numpy as np
import argparse
from pathlib import Path

def load_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def convert_to_json_format(data, max_frames=50):
    """Convert pickle data to JSON format for web viewer"""
    json_data = []
    
    if isinstance(data, list):
        # Frame-level data
        for i, frame in enumerate(data[:max_frames]):
            boxes = frame.get('boxes_lidar', [])
            scores = frame.get('score', [])
            names = frame.get('name', [])
            
            frame_data = {
                'frame_id': int(frame.get('frame_id', i)),
                'sequence_name': frame.get('sequence_name', 'unknown'),
                'boxes': []
            }
            
            for j, box in enumerate(boxes):
                if len(box) >= 7:
                    # box format: [x, y, z, l, w, h, heading]
                    box_data = {
                        'center': [float(box[0]), float(box[1]), float(box[2])],
                        'size': [float(box[3]), float(box[4]), float(box[5])],
                        'rotation': float(box[6]),
                        'score': float(scores[j]) if j < len(scores) else 0.5,
                        'class': str(names[j]) if j < len(names) else 'Vehicle'
                    }
                    frame_data['boxes'].append(box_data)
            
            json_data.append(frame_data)
    
    return json_data

def main():
    parser = argparse.ArgumentParser(description='Prepare data for web visualization')
    parser.add_argument('--detection', type=str, required=True,
                       help='Path to detection result pickle')
    parser.add_argument('--refined', type=str, required=True,
                       help='Path to refined result pickle')
    parser.add_argument('--output_dir', type=str, default='web_visualizer/data',
                       help='Output directory for JSON files')
    parser.add_argument('--max_frames', type=int, default=50,
                       help='Maximum number of frames to export')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading detection data...")
    detection_data = load_pkl(args.detection)
    
    print("Loading refined data...")
    refined_data = load_pkl(args.refined)
    
    print(f"Converting data (max {args.max_frames} frames)...")
    detection_json = convert_to_json_format(detection_data, args.max_frames)
    refined_json = convert_to_json_format(refined_data, args.max_frames)
    
    # Save JSON files
    detection_output = output_dir / 'detection_data.json'
    refined_output = output_dir / 'refined_data.json'
    
    print(f"Saving detection data to {detection_output}...")
    with open(detection_output, 'w') as f:
        json.dump(detection_json, f, indent=2)
    
    print(f"Saving refined data to {refined_output}...")
    with open(refined_output, 'w') as f:
        json.dump(refined_json, f, indent=2)
    
    # Create summary
    summary = {
        'total_frames': len(detection_json),
        'detection': {
            'total_boxes': sum(len(f['boxes']) for f in detection_json),
            'avg_boxes_per_frame': sum(len(f['boxes']) for f in detection_json) / len(detection_json) if detection_json else 0,
            'avg_score': sum(b['score'] for f in detection_json for b in f['boxes']) / sum(len(f['boxes']) for f in detection_json) if sum(len(f['boxes']) for f in detection_json) > 0 else 0
        },
        'refined': {
            'total_boxes': sum(len(f['boxes']) for f in refined_json),
            'avg_boxes_per_frame': sum(len(f['boxes']) for f in refined_json) / len(refined_json) if refined_json else 0,
            'avg_score': sum(b['score'] for f in refined_json for b in f['boxes']) / sum(len(f['boxes']) for f in refined_json) if sum(len(f['boxes']) for f in refined_json) > 0 else 0
        }
    }
    
    summary_output = output_dir / 'summary.json'
    with open(summary_output, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("Data preparation complete!")
    print("="*60)
    print(f"\nFiles created:")
    print(f"  - {detection_output}")
    print(f"  - {refined_output}")
    print(f"  - {summary_output}")
    print(f"\nSummary:")
    print(f"  Total frames: {summary['total_frames']}")
    print(f"  Detection boxes: {summary['detection']['total_boxes']}")
    print(f"  Refined boxes: {summary['refined']['total_boxes']}")
    print(f"  Detection avg score: {summary['detection']['avg_score']:.3f}")
    print(f"  Refined avg score: {summary['refined']['avg_score']:.3f}")
    print("\nNext steps:")
    print("  1. Deploy the web_visualizer folder to Netlify")
    print("  2. Open the deployed URL in your browser")
    print("="*60)

if __name__ == '__main__':
    main()
