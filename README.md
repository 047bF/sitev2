# sitev2
DB Creation
create database db_v2;
create user db_user;
alter role db_user password '94617643852';
grant ALL ON DATABASE db_v2 TO db_user;
alter database db_v2 owner to db_user;
