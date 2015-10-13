#!/bin/bash
cp configuration.in configuration
. configuration

# ##################################################
# CHECKING DEPENDENCIES
# ##################################################
echo "Installing required packages..."
packages="gnuplot-x11 dosemu links p7zip"
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
# INSTALLING ETERNA
# ##################################################
echo -n "Installing ETERNA..."
if [ ! -d /ETERNA33 ];then 
    sudo cp util/Eterna/ETERNA33 /
    echo "Done."
else
    echo "Already installed."
fi
