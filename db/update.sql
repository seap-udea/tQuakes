use tQuakes;
/*
alter table Quakes
      add column country varchar(255),
      add column cluster1 varchar(10),
      add column cluster2 varchar(10),
      add column cluster3 varchar(10),
      add column extra1 varchar(255),
      add column extra2 varchar(255),
      add column extra3 varchar(255),
      add column extra4 varchar(255),
      add column extra5 varchar(255);
*/
alter table Stations
      add column extra1 varchar(255),
      add column extra2 varchar(255),
      add column extra3 varchar(255),
      add column extra4 varchar(255),
      add column extra5 varchar(255);

create table Clusters
(
       /*BASIC IDENTIFICATION*/
       clusterid varchar(7),
       /*Types: R85, KG72, KG74, CORSSA, UHR86*/
       cluster_type varchar(20),
       /*Parameters of cluster Method: separated by ;*/
       cluster_pars varchar(255),
       /*Parameters of cluster Method: separated by ;*/
       cluster_results varchar(1500),

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
)
