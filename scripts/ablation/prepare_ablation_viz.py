#!/usr/bin/env python3
"""Prepare ablation study data for web visualization."""

import json
import pickle
import numpy as np
from pathlib import Path
from collections import defaultdict

def load_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def prepare_visualization_data(frames, max_frames=50):
    """Convert frame data to JSON format for visualization."""
    viz_data = []
    
    # Sort by (sequence_name, frame_id) to ensure proper ordering
    frames_sorted = sorted(frames, key=lambda x: (x['sequence_name'], x['frame_id']))
    
    # Take first max_frames
    frames_to_viz = frames_sorted[:max_frames]
    
    for frame in frames_to_viz:
        boxes_list = []
        for i in range(len(frame['score'])):
            box = frame['boxes_lidar'][i]
            boxes_list.append({
                'center': [float(box[0]), float(box[1]), float(box[2])],
                'size': [float(box[3]), float(box[4]), float(box[5])],
                'rotation': float(box[6]),
                'score': float(frame['score'][i]),
                'class': str(frame['name'][i])
            })
        
        viz_data.append({
            'frame_id': int(frame['frame_id']),
            'sequence_name': frame['sequence_name'],
            'boxes': boxes_list
        })
    
    return viz_data

def main():
    ablation_dir = Path('data/waymo_custom/ablation')
    output_dir = Path('web_visualizer/data/ablation')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    split = 'test'
    class_name = 'Vehicle'
    max_frames = 50
    
    ablation_types = ['detection', 'grm_prm', 'grm_prm_crm']
    ablation_names = {
        'detection': 'Detection Only',
        'grm_prm': 'Detection + GRM + PRM',
        'grm_prm_crm': 'Detection + GRM + PRM + CRM (Full)'
    }
    
    print(f"Preparing ablation visualization data...")
    print(f"Max frames: {max_frames}\n")
    
    # Load all data first
    all_data = {}
    for abl_type in ablation_types:
        input_path = ablation_dir / f'{class_name}_{abl_type}_{split}.pkl'
        if not input_path.exists():
            print(f"⚠️  {abl_type}: File not found - {input_path}")
            continue
        all_data[abl_type] = load_pkl(input_path)
    
    # Find common frames across all datasets
    # Create sets of (sequence, frame_id) tuples
    frame_keys = {}
    for abl_type, frames in all_data.items():
        frame_keys[abl_type] = {(f['sequence_name'], f['frame_id']) for f in frames}
    
    # Find intersection of all frame keys
    common_keys = set.intersection(*frame_keys.values())
    print(f"Common frames across all datasets: {len(common_keys)}")
    
    # Sort common keys and take first max_frames
    common_keys_sorted = sorted(list(common_keys))[:max_frames]
    print(f"Using first {len(common_keys_sorted)} frames\n")
    
    # Create lookup dictionaries
    frame_lookup = {}
    for abl_type, frames in all_data.items():
        frame_lookup[abl_type] = {(f['sequence_name'], f['frame_id']): f for f in frames}
    
    summary = {
        'total_frames': len(common_keys_sorted),
        'ablations': {}
    }
    
    for abl_type in ablation_types:
        if abl_type not in all_data:
            continue
            
        print(f"Processing {abl_type}...")
        
        # Extract frames in order of common_keys_sorted
        ordered_frames = [frame_lookup[abl_type][key] for key in common_keys_sorted]
        
        # Prepare visualization data
        viz_data = []
        for frame in ordered_frames:
            boxes_list = []
            for i in range(len(frame['score'])):
                box = frame['boxes_lidar'][i]
                boxes_list.append({
                    'center': [float(box[0]), float(box[1]), float(box[2])],
                    'size': [float(box[3]), float(box[4]), float(box[5])],
                    'rotation': float(box[6]),
                    'score': float(frame['score'][i]),
                    'class': str(frame['name'][i])
                })
            
            viz_data.append({
                'frame_id': int(frame['frame_id']),
                'sequence_name': frame['sequence_name'],
                'boxes': boxes_list
            })
        
        # Calculate statistics
        total_boxes = sum(len(f['boxes']) for f in viz_data)
        all_scores = [box['score'] for f in viz_data for box in f['boxes']]
        avg_score = np.mean(all_scores) if all_scores else 0.0
        
        # Save JSON
        output_path = output_dir / f'{abl_type}_data.json'
        with open(output_path, 'w') as f:
            json.dump(viz_data, f, indent=2)
        
        summary['ablations'][abl_type] = {
            'name': ablation_names[abl_type],
            'total_boxes': total_boxes,
            'avg_boxes_per_frame': total_boxes / len(viz_data),
            'avg_score': avg_score,
            'file': f'{abl_type}_data.json'
        }
        
        print(f"  ✅ {ablation_names[abl_type]}")
        print(f"     Total boxes: {total_boxes}")
        print(f"     Avg boxes/frame: {total_boxes/len(viz_data):.2f}")
        print(f"     Avg score: {avg_score:.3f}")
        print(f"     Saved to: {output_path}\n")
    
    # Save summary
    summary_path = output_dir / 'ablation_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✅ Summary saved to: {summary_path}")
    print(f"\n📊 Ablation Study Results:")
    print(f"{'Stage':<30} {'Boxes':<10} {'Boxes/Frame':<15} {'Avg Score':<10}")
    print("=" * 70)
    
    for abl_type in ablation_types:
        if abl_type in summary['ablations']:
            info = summary['ablations'][abl_type]
            print(f"{info['name']:<30} {info['total_boxes']:<10} "
                  f"{info['avg_boxes_per_frame']:<15.2f} {info['avg_score']:<10.3f}")
    
    print(f"\n🎯 Analysis:")
    if 'detection' in summary['ablations'] and 'grm_prm_crm' in summary['ablations']:
        det_boxes = summary['ablations']['detection']['total_boxes']
        full_boxes = summary['ablations']['grm_prm_crm']['total_boxes']
        diff = full_boxes - det_boxes
        pct = (diff / det_boxes * 100) if det_boxes > 0 else 0
        
        print(f"  Full pipeline adds {diff:+d} boxes ({pct:+.1f}%)")
        
        if 'grm' in summary['ablations']:
            grm_boxes = summary['ablations']['grm']['total_boxes']
            grm_diff = grm_boxes - det_boxes
            print(f"  GRM contribution: {grm_diff:+d} boxes")
        
        if 'grm_prm' in summary['ablations']:
            prm_boxes = summary['ablations']['grm_prm']['total_boxes']
            prm_diff = prm_boxes - summary['ablations'].get('grm', {'total_boxes': det_boxes})['total_boxes']
            print(f"  PRM contribution: {prm_diff:+d} boxes")
        
        if 'grm_prm_crm' in summary['ablations'] and 'grm_prm' in summary['ablations']:
            crm_diff = full_boxes - summary['ablations']['grm_prm']['total_boxes']
            print(f"  CRM contribution: {crm_diff:+d} boxes")
    
    print(f"\n✨ Next step: Open web_visualizer/ablation.html to compare results")

if __name__ == '__main__':
    main()
