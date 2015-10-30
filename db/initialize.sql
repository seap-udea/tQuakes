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
       country varchar(255),
       departamento varchar(255),
       municipio varchar(255),

       /*INTENSITY*/       
       Ml varchar(5),
       Mw varchar(5),

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
       calctime1 varchar(50),
       calctime2 varchar(50),
       calctime3 varchar(50),

       /*ANALYSIS RESULTS*/       
       qsignal varchar(255),
       qphases varchar(1500),

       /*CLUSTER*/       
       cluster1 varchar(10),
       cluster2 varchar(10),
       cluster3 varchar(10),

       /*EXTRA*/
       extra1 varchar(255),       
       extra2 varchar(255),       
       extra3 varchar(255),       
       extra4 varchar(255),       
       extra5 varchar(255),       

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
	station_statusdate datetime,

	/*RESULTS INFORMATION*/
	station_numquakes varchar(6),
	station_score varchar(100),
	
       /*EXTRA*/
       extra1 varchar(255),       
       extra2 varchar(255),       
       extra3 varchar(255),       
       extra4 varchar(255),       
       extra5 varchar(255),       

       /*PRIMARY KEY*/       
       primary key (station_id)
);

create table Clusters
(
       /*BASIC IDENTIFICATION*/
       clusterid varchar(7),
       /*Types: R85, KG72, KG74, CORSSA, UHR86*/
       cluster_type varchar(20),
       /*Parameters of cluster Method: separated by ;*/
       cluster_pars varchar(255),

       /*CHARACTERISTIC QUAKES*/
       /*First quake*/
       firstquakeid varchar(7),
       /*Quake of maximum magnitude*/
       maxquakeid varchar(7),
       /*NUmber of quakes*/
       numquakes varchar(10),

       /*LOCATION AND TIME OF CLUSTER*/
       /*Equivalent properties*/
       qlatequiv varchar(15),
       qlonequiv varchar(15),
       qdepequiv varchar(15),
       Mlequiv varchar(15),
       qjdmean varchar(50),
       qduration varchar(50),

       /*EXTRA*/
       extra1 varchar(255),       
       extra2 varchar(255),       
       extra3 varchar(255),       
       extra4 varchar(255),       
       extra5 varchar(255),       

       /*PRIMARY KEY*/       
       primary key (clusterid)
);
