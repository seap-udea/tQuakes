create user 'tquakes'@'localhost' identified by 'quakes2015';
create database tQuakes;
grant all privileges on tQuakes.* to 'tquakes'@'localhost';
flush privileges;
