#!/bin/bash
if [ -z "$1" ]; then
    echo "No bucket name specified, exiting program.."
    exit 1
else
    BUCKET_NAME=$1
fi

# specify cluster amount
if [ -z "$2" ]; then
    echo "No value for K specified, exiting program.."
    exit 1
else
    K=$2
fi

BASE_DIR=$(pwd \$)
STARTED=`date +%Y-%m-%d.%H:%M:%S` 
SKIP_CLUSTERS=(16 21 22)

{
    { 
        echo "Running run-lightweight-gan.sh script from ${BASE_DIR}" `date`
        echo "Using k=${K} clusters"

        CLUSTER_ID=54

        while [ $CLUSTER_ID -lt $K ];
        do
            # check if datasets shall be skipped
            if [[ " ${SKIP_CLUSTERS[*]} " =~ " ${CLUSTER_ID} " ]]; then
                echo "Skipping training for excluded cluster ${CLUSTER_ID}"
                ((CLUSTER_ID++))
                continue
            fi

            DATASET="v02_k55_c${CLUSTER_ID}"
            echo "using dataset ${DATASET}"
            
            TARGET_DIR="./data/datasets/${DATASET}_root" 
            RESULTS_DIR="./results/transfer_m70_${DATASET}"
            
            if [ -d RESULTS_DIR ]; then
                # skip if model for dataset has already been trained
                echo "Model for ${DATASET} already trained, skipping"
                ((CLUSTER_ID++))
                continue 
            fi

            # copy ds from bucket if not already copied
            if ! [ -d TARGET_DIR ]; then
                gsutil -m cp -r "gs://ba-training-bucket-1/data/datasets/${DATASET}_root" "./data/datasets" || (echo "Error while copying dataset ${DATASET}, skipping" && ((CLUSTER_ID++)) && continue )
                echo "copied dataset ${DATASET}" `date`
            fi

            # copy model to new folder
            mkdir -p "./models/transfer_m70_${DATASET}"
            cp "./models/v01_all_test2_lwgan/model_70.pt" "./models/transfer_m70_${DATASET}"
            echo "copied model to folder" `date`

            echo "starting training" `date`
            # RUN training
            lightweight_gan \
            --name "transfer_m70_${DATASET}" \
            --data "./data/datasets/${DATASET}_root" \
            --image-size 512 \
            --batch-size 32 \
            --disc-output-size 5 \
            --num-train-steps 71001 \
            --calculate-fid-every 1000 || (echo "Error while training, skipping" && ((CLUSTER_ID++)) && continue )

            # next cluster
            ((CLUSTER_ID++))
            
            echo "completed training for ${DATASET}" `date`
        done
    } ; (echo "shutting down" && sudo shutdown)
    echo "training completed for k=${K}" `date`
} > "${BASE_DIR}/logs/${STARTED}_run-lightweight-gan".log 

