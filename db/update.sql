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
/*
alter table Stations
      add column extra1 varchar(255),
      add column extra2 varchar(255),
      add column extra3 varchar(255),
      add column extra4 varchar(255),
      add column extra5 varchar(255);

create table Clusters
(
       //BASIC IDENTIFICATION
       clusterid varchar(7),
       //Types: R85, KG72, KG74, CORSSA, UHR86
       cluster_type varchar(20),
       cluster_pars varchar(255),
       cluster_results varchar(1500),

       firstquakeid varchar(7),
       maxquakeid varchar(7),
       numquakes varchar(10),

       qlatequiv varchar(15),
       qlonequiv varchar(15),
       qdepequiv varchar(15),
       Mlequiv varchar(15),
       qjdmean varchar(50),
       qduration varchar(50),

       extra1 varchar(255),       
       extra2 varchar(255),       
       extra3 varchar(255),       
       extra4 varchar(255),       
       extra5 varchar(255),       

       primary key (clusterid)
)
*/
/*
create table Users (
       -- Basic
       email varchar(100),
       uname varchar(100),
       password varchar(255),

       -- e.g. Nivel de permisos 1, Basic ; 2, Admin.
       ulevel varchar(2),

       -- Extras
       extra1 varchar(255),
       extra2 varchar(255),
       extra3 varchar(255),
       primary key (email)       
);
*/
/*insert ignore into Users (email,uname,password,ulevel) values ('seapudea@gmail.com','SEAP-UdeA',MD5('123'),'2');*/
/*alter table Users add column activate varchar(1);*/
/*insert ignore into Users (email,uname,password,ulevel) values ('jorge.zuluaga@udea.edu.co','Jorge Zuluaga',MD5('zuluaga03'),'1');*/
insert ignore into Users (email,uname,password,ulevel,activate) values ('gloria.moncayo@udea.edu.co','Gloria Moncayo',MD5('moncayo'),'2','1');
insert ignore into Users (email,uname,password,ulevel,activate) values ('gmonsalvem@unal.edu.co','Gaspar Monsalve',MD5('monsalve'),'1','1');
