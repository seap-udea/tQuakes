/*
create user 'tquakes'@'localhost' identified by 'quakes2015';
create database tQuakes;
grant all privileges on tQuakes.* to 'tquakes'@'localhost';
flush privileges;
*/
use tQuakes;

drop table if exists Quakes,Stations;

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

       /*PRIMARY KEY*/       
       primary key (quakeid)
);

create table Stations
(
	/*BASIC IDENTIFICATION*/
	stationid varchar(7),

	/*STATION INFORMATION*/
	stationname varchar(50),
	stationemail varchar(50),
	stationpass varchar(50),
	stationmd5 varchar(50),

	/*STATION INFORMATION*/
	numquakes varchar(6),
	stationscore varchar(100),
	
       /*PRIMARY KEY*/       
       primary key (stationid)
);
