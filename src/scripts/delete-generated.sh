#!/bin/bash
# holds names of folders with generated images
FOLDERS=()

# command to find all result folders (not generated)
# find ./results -type d -regex "./results/transfer_m70_v02_k55_c[0-9][0-9]?" -print0

# command to find all generated folders
# find ./results -type d -name "transfer_m70_v02_k55_c*-generated-71" -print0

# find all folder names according to pattern and store in FOLDERS array
readarray -d '' FOLDERS < <(find ./results -type d -name "transfer_m70_v02_k55_c*-generated-71" -print0)

echo "${FOLDERS[*]}"

for FOLDER_PATH in "${FOLDERS[@]}"
do
    # delete each folder
    echo "Deleted: ${FOLDER_PATH}"
    rm -r ${FOLDER_PATH}
done
echo "Completed removal of generate image folders."
