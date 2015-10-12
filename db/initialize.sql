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
	station_id varchar(20),

	/*USER INFORMATION*/
	station_name varchar(50),
	station_email varchar(50),

	/*STATION INFORMATION*/
	station_arch varchar(255),
	station_nproc int,
	station_mem int,
	station_mac varchar(50),

	/*STATION STATUS*/
	station_receiving tinyint,
	station_status tinyint,

	/*RESULTS INFORMATION*/
	station_numquakes varchar(6),
	station_score varchar(100),
	
       /*PRIMARY KEY*/       
       primary key (station_id)
);
