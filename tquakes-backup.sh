#!/bin/bash
. configuration

if [ "x$1" = "xQuakes" ];then
    tables="Quakes Clusters"
    filename="Quakes"
else
    tables="Users Stations"
    filename="tQuakes"
fi

echo "Dumping..."
mysqldump -u $DBUSER --password="$DBPASSWORD" tQuakes $tables > data/sql/$filename.sql
echo "Compressing..."
p7zip data/sql/$filename.sql
echo "Splitting..."
cd data/sql/dump
rm $filename.sql.7z-*
split -b 1024k ../$filename.sql.7z $filename.sql.7z-
echo "Git adding..."
git add *
cd - &> /dev/null
echo "Done."
