#!/bin/bash
. configuration

sql="select quakeid,astatus,stationid,adatetime,qsignal,qphases from Quakes where astatus+0>0 order by cast(adatetime as datetime) desc;"
mysql -u $DBUSER --password=$DBPASSWORD $DBNAME -e "$sql" 

