#!/bin/bash
# Wrapper script for running nuScenes to DetZero conversion

# Default paths
SOURCE_PATH="/home/aimob/projects/OpenPCDet/data/nuscenes_custom"
OUTPUT_PATH="./data/waymo_8k"
VERSION="v1.0-tak_8k_human_combined"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE_PATH="$2"
            shift 2
            ;;
        --output)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --validate-only)
            VALIDATE_ONLY="--validate-only"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run conversion
cd scripts/conversion

python3 convert_nuscenes_to_detzero.py \
    --source_path "$SOURCE_PATH" \
    --output_path "$OUTPUT_PATH" \
    --version "$VERSION" \
    ${WORKERS:+--workers $WORKERS} \
    ${VALIDATE_ONLY}
