#!/bin/sh
# from tutorial: https://cloud.google.com/compute/docs/gpus/monitor-gpus

BASE_DIR=$(pwd \$)
echo "Running gpu-metrics-setup script from ${BASE_DIR}"

if [ -d "/opt/google" ]; then
    echo "GPU metrics already set up, exiting program.."
    exit 1
fi

# download metrics agent
echo "Downloading metrics agent.."
sudo mkdir -p /opt/google
cd /opt/google
sudo git clone https://github.com/GoogleCloudPlatform/compute-gpu-monitoring.git

# create venv
echo "Creating virual environment.."
cd /opt/google/compute-gpu-monitoring/linux
sudo /opt/conda/bin/virtualenv -p python3 venv
sudo venv/bin/pip install -Ur requirements.txt

# register agent to start on system boot
sudo cp /opt/google/compute-gpu-monitoring/linux/systemd/google_gpu_monitoring_agent_venv.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl --no-reload --now enable /lib/systemd/system/google_gpu_monitoring_agent_venv.service

echo "GPU metrics set up, go to monitoring section"