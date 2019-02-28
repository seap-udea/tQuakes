#!/bin/bash
dirtquakes="users/tquakes/tQuakes"

echo "Copying Storage 1..."
cd /storage1/$dirtquakes
tar cf - . | pv | (cd /storage/$dirtquakes;tar xf -)
cd -
echo "Copying Storage 3..."
cd /storage3/$dirtquakes
tar cf - . | pv | (cd /storage/$dirtquakes;tar xf -)
cd -
echo "Copying Storage 3..."
cd /storage2/
tar cf - tQuakes_old | pv | (cd /storage/users/tquakes;tar xf -)
cd -
