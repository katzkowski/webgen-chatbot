#!/bin/bash
# specify cluster amount
if [ -z "$1" ]; then
    echo "No value for K specified, exiting program.."
    exit 1
else
    K=$1
fi

# specify image amount
if [ -z "$2" ]; then
    echo "No image count specified, exiting program.."
    exit 1
else
    N_IMAGES=$2
fi

BASE_DIR=$(pwd \$)
STARTED=`date +%Y-%m-%d.%H:%M:%S` 

{
    { 
        echo "Running sample-lightweight-gan.sh script from ${BASE_DIR}" `date`

        CLUSTER_ID=0

        while [ $CLUSTER_ID -lt $K ];
        do
            DATASET="transfer_m70_v02_k55_c${CLUSTER_ID}"
            echo "Sampling ${N_IMAGES} for dataset ${DATASET}" `date`

            # sample images
            lightweight_gan --name "${DATASET}" --generate --num-image-tiles "${N_IMAGES}" --generate-types [ema]

            # next cluster
            ((CLUSTER_ID++))
            
            echo "completed sampling for ${DATASET}" `date`
            echo "================================="
        done
    } ; (echo "shutting down" && sudo shutdown)
    echo "sampling completed" `date`
} > "${BASE_DIR}/logs/${STARTED}_sample-lightweight-gan".log 

