#!/bin/bash

#CHECK DAEMON STATUS
if [ -e stop ];then
    echo "Daemon is stopped..."
else
    echo "Daemon is free to run..."

    if ps caux | grep tquakesd &> /dev/null
    then
	echo "Daemon is Runnning..."
	exit 0
    else
	echo "Daemon is not running..."
    fi
fi

#IF DAEMON IS NOT RUNNING CHECK STATUS OF STATION
if python tquakes-teststation.py
then
    echo "All test passed..."
else
    echo "Something failed."
    exit 1
fi
