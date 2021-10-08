#!/bin/sh
BASE_DIR=$(pwd \$)
echo "Running vm-setup script from ${BASE_DIR}"

if [ -z "$1" ]; then
    echo "No bucket name specified, exiting program.."
    exit 1
else
    BUCKET_NAME=$1
fi

if [ -z "$2" ]; then
    echo "No requirements.txt file specified, exiting program.."
    exit 1
else
    REQ_TXT=$2
fi

if [ -z "$3" ]; then
    echo "No dataset specified, exiting program.."
    exit 1
else
    DATASET_NAME=$3
fi

clone_repo () {
    # if dir exists
    if [ -d "./ba-code" ]; then
        echo "Directory ${BASE_DIR}/ba-code already exists"
    else
        # modify the repository if necessary
        echo "Cloning repository into ${BASE_DIR}/ba-code"
        git clone "https://github.com/katzkowski/ba-code.git"
    fi
    cd ./ba-code
}

create_venv () {
    echo "Creating virtual environment"
    if [ -d "${BASE_DIR}/ba-code/venv" ]; then
        echo "Venv at ${BASE_DIR}/ba-code/venv already exists"
    else
        pip install virtualenv
        virtualenv venv
    fi
    echo "Activating venv"
    . venv/bin/activate
    
    echo "Installing requirements from ${REQ_TXT}"
    pip install -r ${REQ_TXT}
}

get_dot_env () {
    echo "Copying file vm.env from bucket ${BUCKET_NAME} and renaming to .env"
    gsutil cp "gs://${BUCKET_NAME}/env/vm.env" "${BASE_DIR}/ba-code/.env"
}


mk_dir_structure () {

    cd "${BASE_DIR}/ba-code"
    echo "Creating directory structure for training"

    if [ -d "./logs" ]; then
        echo "Skipping already existing directory /logs"
    else 
        mkdir ./logs
    fi

    if [ -d "./data" ]; then
        echo "Skipping already existing directory /data"
    else 
        mkdir ./data
    fi

    # create dir structure in /data
    cd ./data
    if [ -d "./datasets" ]; then
        echo "Skipping already existing directory /data/datasets"
    else 
        mkdir ./datasets
    fi

    if [ -d "./models" ]; then
        echo "Skipping already existing directory /data/models"
    else 
        mkdir ./models
    fi

    if [ -d "./plots" ]; then
        echo "Skipping already existing directory /data/plots"
    else 
        mkdir ./plots
    fi

    # print dir tree
    echo "Finished making dir structure, see tree below"
    tree -d "${BASE_DIR}/ba-code" -I "bin|lib|share|pyvenv.cfg" # ignore venv content
}

copy_training_dataset () {

    TARGET_PATH="${BASE_DIR}/ba-code/data/datasets/dataset_${DATASET_NAME}_root"
    if [ -d TARGET_PATH ]; then
        echo "Dataset ${DATASET_NAME} already exists, continuing without copying"
    else
        echo "Copying training dataset ${DATASET_NAME} from bucket ${BUCKET_NAME}"
        gsutil -m cp -r "gs://${BUCKET_NAME}/data/datasets/dataset_${DATASET_NAME}_root" "${BASE_DIR}/ba-code/data/datasets/"
    fi
}

clone_repo
get_dot_env
create_venv
mk_dir_structure
copy_training_dataset

echo "Final directory structure:"
tree -d "${BASE_DIR}/ba-code" -I "bin|lib|share|pyvenv.cfg" # ignore venv content

# setup gpu metrics (external script)
cd "${BASE_DIR}/ba-code"
. src/scripts/gpu-metrics-setup.sh BUCKET_NAME

echo "VM setup completed"
