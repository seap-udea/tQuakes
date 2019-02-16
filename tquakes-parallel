#!/bin/bash
. configuration
. common
. .stationrc

# CHECK IF IT IS ALREADY RUNNING
if [ -e .start ]
then
    echo "Daemon is already running"
    exit 0
fi
touch .start

# ALLOW GITHUB PULL
eval $(keychain --eval id_rsa_seap)

j=0
while [ 1 ]
do
    # CHECK IF STOP SIGNAL HAVE BEEN SENT
    if [ -e stop ];then 
	echo "Stopping."
	touch log/tquakesd-stopped
	exit 0
    else
	rm log/tquakesd-stopped
    fi

    # UPDATE BRANCH
    echo "Updating repository..."
    make pull

    # RUN PROCESS PER EACH PROCESSOR
    for i in $(seq 1 $station_nproc)
    do
	nsleep=$(( ( RANDOM % 10 )  + 1 ))
	echo "Sleeping $nsleep seconds before starting..."
	sleep $nsleep
	python tquakes-pipeline.py &
    done
    
    # WAIT UNTIL PROCESSES END
    wait
    ((j++))
done
