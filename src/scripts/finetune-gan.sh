#!/bin/sh
# set -e # exit script on error

for DATASET in v02_k55_c22_colorful
do
    echo "using dataset ${DATASET}"
    # copy ds from bucket
    gsutil -m cp -r "gs://ba-training-bucket-1/data/datasets/${DATASET}_root" "./data/datasets"
    echo "copied dataset ${DATASET}"

    # copy model to new folder
    mkdir -p "./models/transfer_m70_${DATASET}"
    cp "./models/v01_all_test2_lwgan/model_70.pt" "./models/transfer_m70_${DATASET}"
    echo "copied model to folder"

    echo "starting training"
    # start training
    lightweight_gan \
    --name "transfer_m70_${DATASET}" \
    --data "./data/datasets/${DATASET}_root" \
    --image-size 512 \
    --batch-size 32 \
    --disc-output-size 5 \
    --num-train-steps 71001 \
    --calculate-fid-every 1000
    echo "completed training for ${DATASET}"
done

echo "fine tuning completed"