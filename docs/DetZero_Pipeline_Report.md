# DetZero Vehicle-Only Pipeline Summary

## Environment & Dataset
- Custom Waymo-style val split: 200 frames, 2265 GT boxes; infos now include `sequence_name`, `sample_idx`, `num_points_in_gt` for proper Waymo eval.
- Raw TFRecords symlinked from OpenPCDet outputs. Tracking output limited to vehicle tracks (199 boxes, 1 track).

## Pipeline Flow
1. **Detection**: `CenterPoint` checkpoint `checkpoint_epoch_12.pth`; eval at `detection/output/.../tmp_eval_real2/eval/epoch_12/val/`.
2. **Tracking**: `tracking/tools/run_track.py` produced `data/waymo/tracking/tracking-val-20251201-010923.pkl` and drop set.
3. **Object Prep**: `daemon/prepare_object_data.py` generated Vehicle crops plus placeholders for Ped/Cyc at `data/waymo/refining/{Vehicle,Pedestrian,Cyclist}/nuscenes_custom_val.pkl`.
4. **Refiners**: GRM, PRM, CRM trained sequentially via `refining/tools/train.py` (logs under `refining/log/`); IoU labels in `data/waymo/refining/Vehicle_iou_train.pkl`.
5. **Combine**: `daemon/combine_output.py` produced final track/frame outputs `data/waymo/refining/result/Vehicle_final*.pkl`.

## Performance Metrics
| Stage | Recall@0.3 | Recall@0.5 | Recall@0.7 | Avg objects/sample |
| --- | --- | --- | --- | --- |
| Detection (RCNN) | 0.9753 | 0.8742 | 0.6000 | 52.29 |
| Refiners (GRM+PRM+CRM) | 0.0000 | 0.0000 | 0.0000 | 0.00 (outputs suppressed) |

*The refiners produced no surviving boxes on this small split, so recall/AP remained zero. Larger val sets or looser CRM filters are needed to see improvement.*

## Next Steps
- Increase val set scale (ideally 5×–10× more frames) to feed GRM/PRM/CRM with more tracks and expect recall gains from 0 to 0.2–0.6.
- Optionally run Pedestrian/Cyclist refine pipelines once tracking covers those classes.
- Use `daemon/combine_output.py` (with confidence outputs) to create final detections for evaluation or visualization.
