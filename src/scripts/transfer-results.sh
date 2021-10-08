#!/bin/sh
BASE_DIR=$(pwd \$)
echo "Running transfer-results.sh script from ${BASE_DIR}"

if [ -z "$1" ]; then
    echo "No bucket name specified, exiting program.."
    exit 1
else
    BUCKET_NAME=$1
fi

# copy logs without checking if file exists
gsutil cp -r "${BASE_DIR}/logs/*" "gs://${BUCKET_NAME}/logs"
echo "Copied logs to ${BUCKET_NAME}/logs"

# copy plots without checking if file exists
gsutil cp -r "${BASE_DIR}/data/plots/*" "gs://${BUCKET_NAME}/plots"
echo "Copied plots to ${BUCKET_NAME}/plots"

# copy models without checking if file exists
gsutil cp -r "${BASE_DIR}/data/models/*" "gs://${BUCKET_NAME}/data/models/"
echo "Copied models to ${BUCKET_NAME}/data/models/"

echo "Transferred results to bucket ${BUCKET_NAME}"