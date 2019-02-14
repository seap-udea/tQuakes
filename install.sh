#!/bin/bash
cp configuration.in configuration
. configuration

# ##################################################
# CHECKING DEPENDENCIES
# ##################################################
echo "Installing required packages..."
packages=$PACKAGES_STATION
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
# CONFIGURE GIT
# ##################################################
git --config user.email seapudea@gmail.com
git --config user.name SEAP

# ##################################################
# INSTALLING GOTIC2
# ##################################################
echo -n "Installing GOTIC2..."
if [ ! -e util/gotic2 ];then 
    make -C util/gotic2-source 
    echo "Done."
else
    echo "Already installed."
fi
