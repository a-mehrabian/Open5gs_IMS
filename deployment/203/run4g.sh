#! /bin/bash
echo "======= CHRONOS 4G-VoLTE v1 ======="
# Set environment variables
echo "Setting environment variables"
cd /home/na13/open5gs_ims/
set -a
source .env
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

echo "PWD: $PWD"

# Check if the container is was running and not down
# ????
echo "Downing containers"
# Down 4G eNB
docker-compose -f srsenb.yaml down
docker-compose -f oaienb.yaml down
# USRP reset FPGA
echo "Resetting USRP FPGA"
# docker run -it --privileged docker_srslte ./usr/local/lib/uhd/utils/b2xx_fx3_utils --reset-device
docker run -it --privileged --rm --name fpga_reset docker_srslte ./usr/local/lib/uhd/utils/b2xx_fx3_utils --reset-device


echo "Starting containers"
sleep 1

# Start 4G eNB
# echo "Starting 4G eNB"
docker-compose -f srsenb.yaml up -d
# docker-compose -f oaienb.yaml up -d
#docker-compose -f srsenb.yaml up -d && docker container attach srsenb
