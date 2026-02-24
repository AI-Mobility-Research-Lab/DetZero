#!/bin/bash
# Master script to run the full DetZero pipeline on 8K nuScenes dataset

set -e  # Exit on error

echo "=========================================="
echo "DetZero 8K nuScenes Pipeline"
echo "=========================================="
echo ""

# Configuration
SPLIT="val"
OUTPUT_BASE="output_8k"
DETECTION_OUTPUT="${OUTPUT_BASE}/detection"
TRACKING_OUTPUT="${OUTPUT_BASE}/tracking"
REFINING_OUTPUT="${OUTPUT_BASE}/refining"

# Create output directories
mkdir -p ${DETECTION_OUTPUT}
mkdir -p ${TRACKING_OUTPUT}
mkdir -p ${REFINING_OUTPUT}

# Step 1: Detection
echo "=========================================="
echo "Step 1: Running Detection"
echo "=========================================="
echo "Using pre-trained OpenPCDet model (80 epochs)"
echo "Dataset: 8K nuScenes custom (800 val samples)"
echo ""

python3 run_detection_8k.py \
    --cfg_file detection/tools/cfgs/det_model_cfgs/centerpoint_8k.yaml \
    --ckpt detection/output/centerpoint_8k/checkpoint_epoch_80.pth \
    --batch_size 4 \
    --workers 4 \
    --output_dir ${DETECTION_OUTPUT} \
    --split ${SPLIT}

echo ""
echo "Detection complete! Results saved to ${DETECTION_OUTPUT}"
echo ""

# Step 2: Tracking
echo "=========================================="
echo "Step 2: Running Tracking"
echo "=========================================="
echo "Using DetZero tracker with 8K config"
echo ""

cd tracking
python3 tools/run_track.py \
    --cfg_file tools/cfgs/tk_model_cfgs/detzero_track_8k.yaml \
    --det_result_path ../${DETECTION_OUTPUT}/${SPLIT}_detections.pkl \
    --output_dir ../${TRACKING_OUTPUT} \
    --split ${SPLIT}
cd ..

echo ""
echo "Tracking complete! Results saved to ${TRACKING_OUTPUT}"
echo ""

# Step 3: Prepare object data for refinement
echo "=========================================="
echo "Step 3: Preparing Object Data"
echo "=========================================="
echo "Extracting object crops for refinement training"
echo ""

python3 daemon/prepare_object_data.py \
    --tracking_result ${TRACKING_OUTPUT}/tracking_${SPLIT}.pkl \
    --data_path /home/aimob/projects/OpenPCDet/data/nuscenes_custom \
    --output_path ${REFINING_OUTPUT} \
    --split ${SPLIT} \
    --class_names car truck pedestrian bicycle

echo ""
echo "Object data prepared! Saved to ${REFINING_OUTPUT}"
echo ""

# Step 4: Train refinement modules (GRM, PRM, CRM)
echo "=========================================="
echo "Step 4: Training Refinement Modules"
echo "=========================================="
echo "This will train GRM, PRM, and CRM sequentially"
echo "Estimated time: 6-12 hours"
echo ""

# Train GRM (Geometry Refinement Module)
echo "Training GRM..."
cd refining
python3 tools/train.py \
    --cfg_file tools/cfgs/ref_model_cfgs/grm_8k.yaml \
    --batch_size 8 \
    --epochs 30 \
    --output_dir ../${REFINING_OUTPUT}/grm

# Train PRM (Position Refinement Module)
echo "Training PRM..."
python3 tools/train.py \
    --cfg_file tools/cfgs/ref_model_cfgs/prm_8k.yaml \
    --batch_size 8 \
    --epochs 30 \
    --output_dir ../${REFINING_OUTPUT}/prm

# Train CRM (Confidence Refinement Module)
echo "Training CRM..."
python3 tools/train.py \
    --cfg_file tools/cfgs/ref_model_cfgs/crm_8k.yaml \
    --batch_size 8 \
    --epochs 30 \
    --output_dir ../${REFINING_OUTPUT}/crm

cd ..

echo ""
echo "Refinement training complete!"
echo ""

# Step 5: Run refinement inference
echo "=========================================="
echo "Step 5: Running Refinement Inference"
echo "=========================================="
echo ""

cd refining
python3 tools/test.py \
    --tracking_result ../${TRACKING_OUTPUT}/tracking_${SPLIT}.pkl \
    --grm_ckpt ../${REFINING_OUTPUT}/grm/checkpoint_best.pth \
    --prm_ckpt ../${REFINING_OUTPUT}/prm/checkpoint_best.pth \
    --crm_ckpt ../${REFINING_OUTPUT}/crm/checkpoint_best.pth \
    --output_dir ../${REFINING_OUTPUT}/results \
    --split ${SPLIT}
cd ..

echo ""
echo "Refinement complete! Results saved to ${REFINING_OUTPUT}/results"
echo ""

# Step 6: Combine results
echo "=========================================="
echo "Step 6: Combining Results"
echo "=========================================="
echo ""

python3 daemon/combine_output.py \
    --geo_path ${REFINING_OUTPUT}/results/Vehicle_geometry_${SPLIT}.pkl \
    --pos_path ${REFINING_OUTPUT}/results/Vehicle_position_${SPLIT}.pkl \
    --conf_path ${REFINING_OUTPUT}/results/Vehicle_confidence_${SPLIT}.pkl \
    --output_path ${REFINING_OUTPUT}/results \
    --split ${SPLIT}

echo ""
echo "=========================================="
echo "Pipeline Complete!"
echo "=========================================="
echo ""
echo "Results:"
echo "  Detection:  ${DETECTION_OUTPUT}/${SPLIT}_detections.pkl"
echo "  Tracking:   ${TRACKING_OUTPUT}/tracking_${SPLIT}.pkl"
echo "  Refinement: ${REFINING_OUTPUT}/results/Vehicle_final_${SPLIT}.pkl"
echo ""
echo "Next steps:"
echo "  1. Evaluate results: cd evaluator && python3 detzero_eval.py ..."
echo "  2. Visualize: python3 visualize_3d_comparison.py ..."
echo "  3. Generate web viz: python3 prepare_ablation_viz.py"
echo ""
