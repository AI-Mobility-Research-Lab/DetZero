#!/usr/bin/env python3
"""Generate ablation study data - compare Detection vs GRM+PRM vs GRM+PRM+CRM."""

import pickle
import numpy as np
from pathlib import Path
from collections import defaultdict

def load_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def save_pkl(data, path):
    with open(path, 'wb') as f:
        pickle.dump(data, f)

def convert_to_frame_format(track_data):
    """Convert track data from seq->obj_id dict format into frame-level list format."""
    frame_res_list = []
    order_map = defaultdict(list)

    for tk_id, tk_info in track_data.items():
        sample_idx = tk_info['sample_idx']
        for i, sa_idx in enumerate(sample_idx):
            order_map[sa_idx].append([tk_id, i])

    frames = list(order_map.keys())
    for frm_id in frames:
        map_temp = np.stack(order_map[frm_id])
        obj_ids, orders = map_temp[:, 0], map_temp[:, 1].astype(int)

        seq = track_data[obj_ids[0]]['sequence_name']
        pose = track_data[obj_ids[0]]['pose'][orders[0]]
        obj_num = len(obj_ids)

        boxes_lidar = np.zeros((obj_num, 7), dtype=np.float32)
        score = np.zeros((obj_num), dtype=np.float32)
        name = np.full(obj_num, 'none', dtype=object)

        for i, obj_id in enumerate(obj_ids):
            idx = orders[i]
            boxes_lidar[i] = track_data[obj_id]['boxes_lidar'][idx]
            score[i] = track_data[obj_id]['score'][idx]
            name[i] = track_data[obj_id]['name'][idx]

        frame_res_list.append({
            'sequence_name': seq,
            'frame_id': int(frm_id),
            'name': name,
            'score': score,
            'boxes_lidar': boxes_lidar,
            'pose': pose
        })

    return frame_res_list

def main():
    root_path = Path('data/waymo_custom/refining')
    result_path = root_path / 'result'
    split = 'test'
    class_name = 'Vehicle'

    print(f"Generating 3-way ablation study...")
    print(f"Comparing: Detection | GRM+PRM | GRM+PRM+CRM\n")
    
    # Load individual module outputs
    geo_path = result_path / f'{class_name}_geometry_{split}.pkl'
    pos_path = result_path / f'{class_name}_position_{split}.pkl'
    conf_path = result_path / f'{class_name}_confidence_{split}.pkl'
    
    print(f"Loading module outputs...")
    print(f"  GRM: {geo_path}")
    geo_res = load_pkl(geo_path)
    
    print(f"  PRM: {pos_path}")
    pos_res = load_pkl(pos_path)
    
    print(f"  CRM: {conf_path}")
    conf_res = load_pkl(conf_path)
    
    # Load detection baseline
    det_path = Path('detection/output/baseline_vehicle_test.pkl')
    print(f"  Detection: {det_path}")
    det_res = load_pkl(det_path)
    print(f"    {len(det_res)} frames\n")
    
    seq_names = list(pos_res.keys())
    
    # Create ablation variants
    ablations = {}
    
    # 1. Detection only (baseline)
    print("1. Baseline: Detection only")
    ablations['detection'] = det_res
    
    # 2. GRM + PRM (no CRM)
    print("2. GRM + PRM (without CRM)")
    grm_prm_dict = defaultdict(dict)
    for seq in seq_names:
        for obj in pos_res[seq].keys():
            grm_prm_dict[seq][obj] = pos_res[seq][obj].copy()
            # Get geometry from GRM
            boxes_geo = np.concatenate(geo_res[seq][obj]['boxes_lidar'], axis=0)
            # Get position from PRM
            grm_prm_dict[seq][obj]['boxes_lidar'] = np.array(pos_res[seq][obj]['boxes_lidar'])
            # Combine: PRM position + GRM dimensions
            grm_prm_dict[seq][obj]['boxes_lidar'][:, 3:6] = boxes_geo[:, 3:6]
            # Use PRM score (not CRM)
            # Set sample_idx for conversion
            grm_prm_dict[seq][obj]['sample_idx'] = \
                np.array([str(x) for x in pos_res[seq][obj]['frame_id']])
    
    # Convert track dict to frame list
    grm_prm_track_list = {}
    for seq in grm_prm_dict:
        for obj_id, obj_data in grm_prm_dict[seq].items():
            grm_prm_track_list[f"{seq}/{obj_id}"] = obj_data
    ablations['grm_prm'] = convert_to_frame_format(grm_prm_track_list)
    
    # 3. Full pipeline (GRM + PRM + CRM)
    print("3. Full pipeline (GRM + PRM + CRM)")
    full_dict = defaultdict(dict)
    for seq in seq_names:
        for obj in pos_res[seq].keys():
            full_dict[seq][obj] = pos_res[seq][obj].copy()
            # Get geometry from GRM
            boxes_geo = np.concatenate(geo_res[seq][obj]['boxes_lidar'], axis=0)
            # Get position from PRM
            full_dict[seq][obj]['boxes_lidar'] = np.array(pos_res[seq][obj]['boxes_lidar'])
            # Combine: PRM position + GRM dimensions
            full_dict[seq][obj]['boxes_lidar'][:, 3:6] = boxes_geo[:, 3:6]
            
            # Use CRM score if available
            if seq in conf_res and obj in conf_res[seq] and 'new_score' in conf_res[seq][obj]:
                full_dict[seq][obj]['score'] = conf_res[seq][obj]['new_score']
            
            # Set sample_idx for conversion
            full_dict[seq][obj]['sample_idx'] = \
                np.array([str(x) for x in pos_res[seq][obj]['frame_id']])
    
    # Convert track dict to frame list
    full_track_list = {}
    for seq in full_dict:
        for obj_id, obj_data in full_dict[seq].items():
            full_track_list[f"{seq}/{obj_id}"] = obj_data
    ablations['grm_prm_crm'] = convert_to_frame_format(full_track_list)
    
    # Save ablation results
    output_dir = Path('data/waymo_custom/ablation')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    for name, data in ablations.items():
        output_path = output_dir / f'{class_name}_{name}_{split}.pkl'
        save_pkl(data, output_path)
        
        # Print statistics
        total_boxes = sum(len(frame['score']) for frame in data)
        all_scores = np.concatenate([frame['score'] for frame in data])
        
        print(f"\n{name.upper()}:")
        print(f"  Total boxes: {total_boxes}")
        print(f"  Avg boxes/frame: {total_boxes/len(data):.2f}")
        print(f"  Score range: [{all_scores.min():.3f}, {all_scores.max():.3f}]")
        print(f"  Avg score: {all_scores.mean():.3f}")
        print(f"  Saved to: {output_path}")
    
    print("\n✅ Ablation data generated successfully!")
    print(f"\nNext steps:")
    print(f"1. Generate visualization data:")
    print(f"   python prepare_ablation_viz.py")
    print(f"2. View in web visualizer with 4-panel comparison")

if __name__ == '__main__':
    main()
