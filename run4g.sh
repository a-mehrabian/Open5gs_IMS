#! /bin/bash
echo "======= CHRONOS 4G-VoLTE v1 ======="
UPF_IP=$(grep -oP 'UPF_IP=\K[^ ]+' .env)
UE_IPV4_INTERNET=$(grep -oP 'UE_IPV4_INTERNET=\K[^ ]+' .env)
UE_IPV4_IMS=$(grep -oP 'UE_IPV4_IMS=\K[^ ]+' .env)
# Check Requirements:
echo "Checking requirements..."
echo "======================="
if ! command -v jq &> /dev/null
then
    echo "jq is not installed. Installing jq..."
    sudo apt update
    sudo apt install -y jq
else
    echo "All requirements satisfied."
fi

echo "======================="
# Set environment variables
echo "Applying environment variables..."
echo "======================="
set -a
source .env
sudo ufw disable
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -P FORWARD ACCEPT
echo "The network and firewall settings applied"
echo "Performance Mode: ON " | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

echo "======================="
if docker ps | grep docker_open5gs > /dev/null
then
    echo "Container running"
    echo "Stopping the containers..."
    docker compose down
    echo "======================="
fi
# Start 4G Core Network + IMS + SMS over SGs
echo "Starting 4G Core Network"
echo "======================="
docker compose up -d
docker compose logs -f 


# Route UE traffic to the docker interface
echo "======================="
sudo ip route add $UE_IPV4_INTERNET via $UPF_IP
sudo ip route add $UE_IPV4_IMS via $UPF_IP
echo "UE traffic routed to the docker interface"

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