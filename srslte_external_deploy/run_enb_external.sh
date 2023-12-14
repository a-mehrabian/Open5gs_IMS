#!/bin/bash

# Apply the environment variables
echo "Applying environment variables..."
echo "======================="
set -a
source .env
# Set the variables
CORE_IP=$(grep -oP 'CORE_IP=\K[^ ]+' .env)
eNB_ID=$(grep -oP 'eNB_ID=\K[^ ]+' .env)
USRP_TYPE=$(grep -oP 'USRP_TYPE=\K[^ ]+' .env)
# Ping the core network
echo "CORE_IP: $CORE_IP"
echo "Test the connection to the core network..."
if ping -c 1 $CORE_IP &> /dev/null
then
    echo "Connection to the core network is OK"
else
    echo "Connection to the core network is not OK"
    echo "Please check the CORE_IP in the .env file"
    exit
fi
echo "======================="
# Apply the network and firewall settings
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -P FORWARD ACCEPT
sudo ip route add 172.22.0.0/24 via $CORE_IP
echo "The network and firewall settings applied"
echo "Performance Mode: ON " | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo "======================="
if docker ps | grep docker_srslte:external > /dev/null
then
    echo "Container is running"
    echo "Stopping the container..."
    docker compose down
    echo "======================="
fi
# is teh usrp type is u220, then run the u220 script
if [ "$USRP_TYPE" == "U220" ] ;then
    echo "Running the U220 script..."
    echo "======================="
    docker run -it --privileged --rm --name fpga_reset docker_srslte:external ./usr/local/lib/uhd/utils/b2xx_fx3_utils --reset-device
    echo "======================="
fi
echo "Starting eNB ${eNB_ID}..."
echo "======================="
echo "Freeing up space in docker_srslte:external"
docker run -it --rm docker_srslte:external bash -c "rm -rf /mnt/srslte/logs/*"
docker compose up -d
docker compose logs -f
# If the user type ctrl+c, ask if he wants to stop the container or restart the script or skip by 3 option
echo "======================="
echo "Enter your option: "
echo "======================="
echo "1. Stop the container"
echo "2. Restart the script"
echo "Enter to skip"
read answer
if [ "$answer" == "1" ] ;then
    echo "Stopping the container..."
    docker compose down
elif [ "$answer" == "2" ] ;then
    echo "Restarting the script..."
    $0
else
    echo "The container is still running"
fi
# End of script
echo "======================="