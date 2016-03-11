#!/bin/bash

# ##################################################
# CHECKING DEPENDENCIES
# ##################################################
echo "Installing required packages..."
packages="git"
packinst=""
for package in $packages
do
    echo -en "\tChecking for $package..."
    if dpkg -s $package &> /dev/null;then
	echo "Installed."
    else
	echo "Queued."
	packinst="$packinst $package"
    fi
done

if [ "x$packinst" != "x" ];then
    echo -e "Packages to install:\n\t$packinst"
    sudo apt-get install $packinst
else
    echo -e "No packages required to be installed."
fi
 
# ##################################################
# CLONE STATION BRANCH
# ##################################################
echo "Cloning tQuakes station package..."
if [ ! -d tQuakes ];then
    git clone --branch station --single-branch http://github.com/seap-udea/tQuakes.git
    rm tQuakes/.git
else
    echo -e "\ttQuakes already downloaded.  Updating."
    cd tQuakes
    make pull
    cd -
fi

# ##################################################
# INSTALLING PACKAGE
# ##################################################
cd tQuakes
make install

# ##################################################
# PREREGISTERING STATION
# ##################################################
python tquakes-station.py
. .stationrc

# ##################################################
# SSH KEY
# ##################################################
echo "Generating ssh keys..."
if [ ! -e $HOME/.ssh/id_rsa.pub ];then
    ssh-keygen -t rsa -N "" -f $HOME/.ssh/id_rsa
    echo "Key generated."
else
    echo "Key already generated."
fi
station_key=$(cat $HOME/.ssh/id_rsa.pub)

# ##################################################
# INFORMATION REQUIRED FOR NEXT STEP
# ##################################################
echo;echo
echo "Your station is ready to be used.  Please register it using:"
echo
echo "ID: $station_id"
echo
echo "Public key:"
echo
echo $station_key
echo;echo
