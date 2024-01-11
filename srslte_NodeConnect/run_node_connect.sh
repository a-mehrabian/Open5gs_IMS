#!/bin/bash

# Apply the environment variables
echo "Applying environment variables..."
echo "======================="
echo "Changing the directory to srslte_NodeConnect..."
cd /home/humanitas/open5gs_ims/srslte_NodeConnect
echo "PWD: $(pwd)"
echo "======================="
set -a
source .env
# Set the variables
CORE_IP=$(grep -oP 'CORE_IP=\K[^ ]+' .env)
eNB_ID=$(grep -oP 'eNB_ID=\K[^ ]+' .env)
USRP_TYPE=$(grep -oP 'USRP_TYPE=\K[^ ]+' .env)
COMPONENT_NAME=$(grep -oP 'COMPONENT_NAME=\K[^ ]+' .env)
# Ping the core network
if [ "$COMPEONENT_NAME" == "enb" ]; then
    echo "CORE_IP: $CORE_IP"
    echo "Test the connection to the core network..."
    if ping -c 1 $CORE_IP &> /dev/null
    then
        echo "Connection to the core network is OK"
    else
        while true; do
            echo "Connection to the core network is not OK"
            echo "Please check the CORE_IP in the .env file"
            sleep 10
            if ping -c 1 $CORE_IP &> /dev/null; then
                echo "Connection to the core network is OK"
                break
            fi
        done
    fi
fi

echo "======================="
# Apply the network and firewall settings
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -P FORWARD ACCEPT
# if the component name is enb, then apply the following settings 
if [ "$COMPONENT_NAME" == "enb" ]; then
    sudo ip route add 172.22.0.0/24 via $CORE_IP
fi
echo "The network and firewall settings applied"
echo "Performance Mode: ON " | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo "======================="
if docker ps | grep docker_srslte:connect > /dev/null
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
    docker run -it --privileged --rm --name fpga_reset docker_srslte:connect ./usr/local/lib/uhd/utils/b2xx_fx3_utils --reset-device
    echo "======================="
fi

echo "Starting $COMPONENT_NAME..."
echo "======================="
echo "Freeing up space in docker_srslte:connect"
docker run -it --rm docker_srslte:connect bash -c "rm -rf /mnt/srslte/logs/*"
docker compose up -d

# if the component name is ue 
if [ "$COMPONENT_NAME" == "ue" ]; then
    NODE_CONNECT_IP=""
    while [ -z "$NODE_CONNECT_IP" ]; do
        echo "======================="
        echo "Waiting for UE to connect..."
        # Assuming "node_connect" is the name of the interface when the UE is connected
        NODE_CONNECT_IP=$(ifconfig node_connect | awk '/inet / {print $2}')
        echo "======================="
        sleep 5
    done
    echo "======================="
    # echo "NODE_CONNECT_IP: $NODE_CONNECT_IP"
    echo "UE is connected with IP: $NODE_CONNECT_IP"
    # Add IP route when UE is connected
    sudo ip route add 172.22.0.0/24 via $NODE_CONNECT_IP
    sudo ip route delete default
    sudo ip route add default via $NODE_CONNECT_IP
    echo "Route added"
    echo "======================="
fi | docker compose logs -f

wait
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
