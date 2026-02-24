## DetZero Custom Data Refinement – Current Evaluation Issue

### Summary

On the custom `waymo_custom` dataset, the current DetZero refinement pipeline (tracking + GRM + PRM + CRM) does **not** improve detection metrics over the baseline CenterPoint detector. For `Vehicle` on the `test` split, refinement actually degrades performance from near-perfect AP to almost zero AP when evaluated with the Waymo 3D detection metrics.

### Environment and Data

- Repository: `DetZero` (`/home/aimob/projects/DetZero`)
- Custom dataset root: `data/waymo_custom`
  - Processed infos: `waymo_infos_{train,val,test}.pkl`
  - Processed points: `waymo_custom_processed_data/segment-*/%04d.npy`
  - Tracking results: `data/waymo_custom/tracking/*.pkl`
  - Refining outputs: `data/waymo_custom/refining/result/*`
- Detector: CenterPoint (`centerpoint_1sweep_custom.yaml`, epoch 30 checkpoint)
- Evaluator: `evaluator/detzero_eval.py` (Waymo Open Dataset 3D metrics, IoU in 3D)

### Baseline vs Refined Results (Vehicle, `test` split)

All numbers below are for the `Vehicle` class only, using 3D mAP/mAPH on the custom `test` split (`waymo_infos_test.pkl`).

| Model                  | Split | L1 AP   | L1 APH  | L2 AP   | L2 APH  |
|------------------------|-------|---------|---------|---------|---------|
| CenterPoint baseline   | test  | 0.9770  | 0.9768  | 0.9770  | 0.9768  |
| DetZero refined (Veh.) | test  | 0.0010  | 0.0010  | 0.0010  | 0.0010  |

Observations:

- Baseline CenterPoint achieves very high detection quality on the custom test set.
- The refined Vehicle output (`Vehicle_final_frame.pkl`) performs dramatically worse when evaluated as a detection result on the same split.
- This means we currently **cannot demonstrate improvement** from the refining pipeline on this dataset/split.

### How to Reproduce

All commands assume the working directory is the repo root: `/home/aimob/projects/DetZero`.

#### 1. Baseline CenterPoint on `test`

Run CenterPoint with the custom config and checkpoint, evaluating on `DATA_SPLIT.test = test` and saving predictions:

```bash
cd detection/tools

PYTHONPATH=..:../..:$PYTHONPATH \
python3 test.py \
  --cfg_file cfgs/det_model_cfgs/centerpoint_1sweep_custom.yaml \
  --ckpt ../output/det_model_cfgs/centerpoint_1sweep_custom/waymo_custom_noaug/ckpt/checkpoint_epoch_30.pth \
  --extra_tag waymo_custom_noaug_test \
  --save_to_file \
  --set DATA_CONFIG.DATA_PATH ../../data/waymo_custom DATA_CONFIG.DATA_SPLIT.test test
```

This produces:

- `detection/output/det_model_cfgs/centerpoint_1sweep_custom/waymo_custom_noaug_test/eval/epoch_30/test/result.pkl`

#### 2. Filter baseline to `Vehicle` only

```bash
cd /home/aimob/projects/DetZero

python3 - << 'PY'
import pickle, numpy as np
from pathlib import Path

src = Path('detection/output/det_model_cfgs/centerpoint_1sweep_custom/waymo_custom_noaug_test/eval/epoch_30/test/result.pkl')
with src.open('rb') as f:
    frames = pickle.load(f)

veh_frames = []
for d in frames:
    names = np.asarray(d['name'])
    mask = names == 'Vehicle'
    if not mask.any():
        veh_frames.append({
            'sequence_name': d['sequence_name'],
            'frame_id': d['frame_id'],
            'name': np.array([], dtype=object),
            'score': np.array([], dtype=np.float32),
            'boxes_lidar': np.zeros((0, 7), dtype=np.float32),
            'pose': d['pose'],
        })
        continue
    veh_frames.append({
        'sequence_name': d['sequence_name'],
        'frame_id': d['frame_id'],
        'name': names[mask],
        'score': np.asarray(d['score'])[mask],
        'boxes_lidar': np.asarray(d['boxes_lidar'])[mask],
        'pose': d['pose'],
    })

out = Path('detection/output/baseline_vehicle_test.pkl')
with out.open('wb') as f:
    pickle.dump(veh_frames, f)
print('Wrote', out)
PY
```

#### 3. Evaluate baseline Vehicle vs GT

```bash
cd evaluator

PYTHONPATH=..:$PYTHONPATH \
python3 detzero_eval.py \
  --det_result_path ../detection/output/baseline_vehicle_test.pkl \
  --gt_info_path ../data/waymo_custom/waymo_infos_test.pkl \
  --class_name Vehicle \
  --evaluate_metrics object
```

This prints the baseline Vehicle AP/APH (≈ 0.977).

#### 4. Refined Vehicle results

Assuming the refining pipeline has already been run on `test`, the combined Vehicle results are in:

- `data/waymo_custom/refining/result/Vehicle_final_frame.pkl`

Normalize this for evaluation:

```bash
cd /home/aimob/projects/DetZero

python3 - << 'PY'
import pickle
from pathlib import Path

src = Path('data/waymo_custom/refining/result/Vehicle_final_frame.pkl')
with src.open('rb') as f:
    frames = pickle.load(f)

def fix_frame(d):
    keys = ['sequence_name','frame_id','name','score','boxes_lidar','pose']
    return {k: d[k] for k in keys}

fixed = [fix_frame(d) for d in frames]

out = Path('detection/output/refined_vehicle_test.pkl')
with out.open('wb') as f:
    pickle.dump(fixed, f)
print('Wrote', out)
PY
```

#### 5. Evaluate refined Vehicle vs GT

```bash
cd evaluator

PYTHONPATH=..:$PYTHONPATH \
python3 detzero_eval.py \
  --det_result_path ../detection/output/refined_vehicle_test.pkl \
  --gt_info_path ../data/waymo_custom/waymo_infos_test.pkl \
  --class_name Vehicle \
  --evaluate_metrics object
```

This prints the refined Vehicle AP/APH (≈ 0.001).

### Current Status and Next Steps

- The evaluation pipeline itself runs end-to-end and is reproducible via the commands above.
- On the current custom `test` split and Vehicle class, refinement significantly **hurts** detection metrics compared to the baseline detector.
- The dataset splits for other custom datasets (e.g. `argo2`) have been checked and are sequence-level in terms of `seq_id`, so the degradation is unlikely to be caused solely by non-contiguous sequences in the evaluation split.

Suggested follow-ups (not yet done):

- Verify that GRM/PRM/CRM inference and combination for the `test` split exactly align with `waymo_infos_test.pkl` (sequence naming, frame indexing, and split usage).
- Inspect a few sample frames comparing baseline vs refined boxes against GT to understand whether refinement is misplacing boxes, overscoring low-IoU boxes, or otherwise diverging in a systematic way.

