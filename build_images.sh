#!/bin/bash

echo "Choose an option:"
echo "1: Build basic (Core network)"
echo "2: Build eNB"
echo "3: Build all (CN + eNB)"
echo "4: Update with cache for all images"
read option

case $option in
  1)
    # Build basic (Core network)
    cd base
    docker build --no-cache --force-rm -t docker_open5gs .
    
    cd ../ims_base
    docker build --no-cache --force-rm -t docker_kamailio .
    ;;
    
  2)
    # Build eNB
    cd srslte
    docker build --no-cache --force-rm -t docker_srslte .
    
    cd ../srslte_external_deploy
    docker compose build

    cd ../srslte_NodeConnect
    docker compose build
    ;;

  3)
    # Build all (CN + eNB)
    cd base
    docker build --no-cache --force-rm -t docker_open5gs .
    
    cd ../ims_base
    docker build --no-cache --force-rm -t docker_kamailio .

    cd ../srslte
    docker build --no-cache --force-rm -t docker_srslte .

    cd ../srslte_external_deploy
    docker compose build

    cd ../srslte_NodeConnect
    docker compose build
    ;;

  4)
    # Update with cache for all images
    cd base
    docker build -t docker_open5gs .
    
    cd ../ims_base
    docker build -t docker_kamailio .

    cd ../srslte
    docker build -t docker_srslte .

    cd ../srslte_external_deploy
    docker compose build

    cd ../srslte_NodeConnect
    docker compose build
    ;;

  *)
    echo "Invalid option"
    ;;
esac

# Clear junk images
docker image prune --force
docker compose build