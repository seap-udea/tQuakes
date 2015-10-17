#!/bin/bash
. configuration

echo "Installing keys..."
cp stations/authorized_keys $HOMEDIR/$TQUSER/.ssh
chown $TQUSER.$TQUSER $HOMEDIR/$TQUSER/.ssh/authorized_keys
chmod og-rwx $HOMEDIR/$TQUSER/.ssh/authorized_keys

echo "Receiving from all stations..."
mysql -u $DBUSER --password=$DBPASSWORD tQuakes -e 'update Stations set station_receiving="1"'

echo "Done."
