CREATE DATABASE USERS;
USE USERS;

CREATE TABLE user(
   username varchar(100) not null,
   email varchar(100) not null,
   role varchar(100) not null,
   password varchar(100) not null,
   PRIMARY KEY(username), UNIQUE(email)
);


insert into user(username,email,role,password)
values("Me" , "Ani@Secure.com" , "Admin" , "$argon2id$v=19$m=16,t=2,p=1$VXc5eWZNR1phb1JLN0hGcQ$VqDcMJuxpPLxba7FEwWRjg");


CREATE TABLE agent(
   uuid varchar(255) not null,
   active boolean not null,
   PRIMARY KEY(uuid) 
);


insert into agent(uuid,active)
values("DESKTOP-8Q34ERD2" , "1");

insert into agent(uuid,active)
values("DESKTOP-32AEZ58" , "0");


CREATE TABLE userpass(
   id int not null AUTO_INCREMENT,
   uname varchar(100) not null,
   passwordsecond varchar(100) not null,
   passwordthird varchar(100) not null, 
   PRIMARY KEY(id), FOREIGN KEY(uname) REFERENCES user(username), UNIQUE(uname)
);

insert into userpass(uname, passwordsecond, passwordthird)
values("Me","$argon2id$v=19$m=16,t=2,p=1$VXc5eWZNR1phb1JLN0hGcQ$VqDcMJuxpPLxba7FEwWRjg","$argon2id$v=19$m=16,t=2,p=1$VXc5eWZNR1phb1JLN0hGcQ$VqDcMJuxpPLxba7FEwWRjg");

CREATE TABLE logs(
   id int not null AUTO_INCREMENT,
   createdat DATETIME not null,
   logtext TEXT(32768) not null, 
   PRIMARY KEY(id)
);

insert into logs(createdat, logtext)
values(now() , "This is a test log");