#!/bin/bash
if [ -z "$1" ]; then
    echo "No bucket name specified, exiting program.."
    exit 1
else
    BUCKET_NAME=$1
fi

# exit on error
set -e

BASE_DIR=$(pwd \$)
NOW=`date +%Y-%m-%d.%H:%M:%S` 

# specify cluster amount
K=55
{ 
    echo "Running transfer-datasets.sh script from ${BASE_DIR}"
    echo "Using k=${K} clusters"

    for CLUSTER_ID in {0..54};
    do
        DATASET_NAME="v02_k55_c${CLUSTER_ID}"

        # create dataset
        echo "Running dataset creator ${DATASET_NAME}.."
        python -m src run_creator \
            False $DATASET_NAME v01_all_run2_pca90 $K $CLUSTER_ID

        # copy dataset to glcoud, overwrite if exits
        echo "Copying ${DATASET_NAME} to bucket.."
        gsutil -m cp -r "${BASE_DIR}/data/datasets/${DATASET_NAME}_root" "gs://${BUCKET_NAME}/data/datasets"

        echo "Copied ${DATASET_NAME} to ${BUCKET_NAME}/data/datasets";
        echo "======================================================"
    done

    echo "Finished transferring ${K} clusters" 
} > "${BASE_DIR}/logs/"`date '+%Y-%m-%d_%H-%M-%S'`"_transfer-datasets_K${K}".log