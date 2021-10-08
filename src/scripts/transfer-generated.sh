#!/bin/bash
# holds names of folders with generated images
FOLDERS=()

# check if bucket name specified
if [ -z "$1" ]; then
    echo "No bucket name specified, exiting program.."
    exit 1
else
    BUCKET_NAME=$1
fi

# command to find all result folders (not generated)
# find ./results -type d -regex "./results/transfer_m70_v02_k55_c[0-9][0-9]?" -print0

# command to find all generated folders
# find ./results -type d -name "transfer_m70_v02_k55_c*-generated-71" -print0

# find all folder names according to pattern and store in FOLDERS array
readarray -d '' FOLDERS < <(find ./results -type d -regex "./results/transfer_m70_v02_k55_c[0-9][0-9]?" -print0)

echo "${FOLDERS[*]}"

for FOLDER_PATH in "${FOLDERS[@]}"
do
    # copy each folder to bucket
    gsutil -m cp -r "${FOLDER_PATH}" "gs://${BUCKET_NAME}/results/"
    echo "Copied generated images from ${FOLDER_PATH} to ${BUCKET_NAME}"
done
echo "Completed transfer of generated images"
