#!/bin/bash
if [ ! -e configuration ];then
    cp configuration.in configuration
fi
. configuration

# ##################################################
# CHECKING DEPENDENCIES
# ##################################################
echo "Installing required packages..."
packages=$PACKAGES_FULL
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
    sudo apt-get update
    sudo apt-get install $packinst
else
    echo -e "No packages required to be installed."
fi
 
# ##################################################
# INSTALLING ETERNA
# ##################################################
echo -n "Installing ETERNA..."
if [ ! -d /ETERNA33 ];then 
    sudo cp -r util/Eterna/ETERNA33 /
    echo "Done."
else
    echo "Already installed."
fi

# ##################################################
# INSTALLING SPICEYPY
# ##################################################
echo "Installing SpiceyPy..."
if ! python -c "import spiceypy" 2> /dev/null
then
    cd util/SpiceyPy
    python setup.py install
    cd -
else
    echo -e "\tSpiceyPy already installed."
fi

# ##################################################
# CREATING tQUAKES USER
# ##################################################
echo -en "Creating tquakes user..."
if [ ! -d $HOMEDIR/$TQUSER ];then
    useradd -m -s /bin/bash -d $HOMEDIR/$TQUSER $TQUSER
    echo "Done." 
else
    echo "user already created."
fi
mkdir -p $HOMEDIR/$TQUSER/.ssh
mkdir -p $HOMEDIR/$TQUSER/tQuakes
touch $HOMEDIR/$TQUSER/.ssh/authorized_keys
chmod -R og-rwx $HOMEDIR/$TQUSER/.ssh
chown -R $TQUSER.$TQUSER $HOMEDIR/$TQUSER/

# ##################################################
# CREATING DATABASE
# ##################################################
echo "Installing database..."
if [ ! -e db/.inidb ];then
    echo -e "\tWhen prompted please use root mysql password."
    mysql -u root -p < db/user.sql
    mysql -u root -p < db/initialize.sql
    make restoreall
    touch db/.inidb
else
    echo "Database already installed."
fi

# ##################################################
# GIT CONFIGURATION
# ##################################################
git config --global core.editor "emacs -nw"
git config --global user.email "seapudea@gmail.com"
git config --global user.name "tQuakes"
