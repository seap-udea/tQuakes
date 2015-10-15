#!/bin/bash
echo "During installation the user password will be prompted."
echo "Installing dependencies..."
sudo apt-get install p7zip mysql-server
echo "create database tQuakes;
use tQuakes;
drop table if exists Quakes;
create table Quakes (
       /*BASIC IDENTIFICATION*/
       quakeid varchar(7),
       quakestr varchar(255),

       /*TIME*/
       qdate varchar(20),
       qtime varchar(20),
       qdatetime varchar(20),
       qjd varchar(50),

       /*LOCATION*/
       qlat varchar(15),
       qlaterr varchar(15),
       qlon varchar(15),
       qlonerr varchar(15),
       qdepth varchar(15),
       qdeptherr varchar(15),
       departamento varchar(255),
       municipio varchar(255),

       /*INTENSITY*/       
       Mw varchar(5),
       Ml varchar(5),

       /*MEASUREMENT PROPERTIES*/       
       numstations varchar(10),
       timerms varchar(10),
       gap varchar(10),

       /*MEASUREMENT STATUS*/       
       status varchar(255),

       /*ANALYSIS VARIABLES*/       
       astatus varchar(255),
       adatetime varchar(255),
       stationid varchar(255),

       /*ANALYSIS RESULTS*/       
       qsignal varchar(255),
       qphases varchar(255),

       /*PRIMARY KEY*/       
       primary key (quakeid)
);" > tQuakes-creation.sql
echo "The MySQL root password will be prompted here..."
mysql -u root -p < tQuakes-creation.sql
p7zip -d tQuakes.sql.7z
mysql -u root -p < tQuakes.sql
echo "Done."
