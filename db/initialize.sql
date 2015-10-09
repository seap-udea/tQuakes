create user 'tquakes'@'localhost' identified by 'quakes2015';
create database tQuakes;
grant all privileges on tQuakes.* to 'tquakes'@'localhost';
flush privileges;

use tQuakes;

drop table if exists Quakes;

create table Quakes (
       quakeid varchar(7),
       qdate varchar(20),
       qtime varchar(20),
       qlat varchar(15),
       qlaterr varchar(15),
       qlon varchar(15),
       qlonerr varchar(15),
       qdepth varchar(15),
       qdeptherr varchar(15),
       Mw varchar(5),
       Ml varchar(5),
       departamento varchar(255),
       municipio varchar(255),
       numstations varchar(10),
       timerms varchar(10),
       gap varchar(10),
       status varchar(255),
       extra1 varchar(255),
       extra2 varchar(255),
       extra3 varchar(255),
       primary key (quakeid)
);
