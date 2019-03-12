#drop  database bughound;
#drop table Attachment;
#drop table BugReport;
#drop table Program;
#drop table Employee;
#drop table FunctionalArea;

create database bughound;
use bughound;

create table FunctionalArea(
    areaName varchar(40) not null,
    primary key (areaName)
);

create table Employee(
    employeeId int(10) not null auto_increment,
    name varchar(40) not null,
    username varchar(40) not null,
    password varchar(40) not null,
    level int(1) not null,
    area varchar(40) not null,
    primary key (employeeID),
    foreign key (area) references FunctionalArea(areaName)  
);

create table Program(
    programId int(10) not null auto_increment,
    name varchar(40) not null,
    version int(3) not null,
    releaseNumber int(3) not null,
    description varchar(200) not null,
    primary key (programID)    
);

create table BugReport(
    reportId int(10) not null auto_increment,
    programId int(10) not null,
    reportType int(10) not null,
    severity int(5) not null,
    summary varchar(400) not null,
    reproducable boolean not null,
    description varchar(400) not null,
    suggestedFix varchar(400) not null,
    reportedBy int(10) not null,
    discoveredDate date not null,
    assignedTo int(10) not null,
    comments varchar(400) not null,
    status int(1) not null,
    priority int(1) not null,
    resolution int(2) not null,
    resolutionVersion int(3) not null,
    resolvedBy int(10) not null,
    resolvedDate date not null,
    testedBy int(10) not null,
    testedDate date not null,
    deferred boolean not null,
    primary key (reportId),
    foreign key (programID) references Program(programId),
    foreign key (reportedBy) references Employee(employeeId),
    foreign key (assignedTo) references Employee(employeeId),
    foreign key (resolvedBy) references Employee(employeeId)      
);

create table Attachment(
    reportId int(10) not null,
    fileName varchar(40) not null,
    file longblob,
    primary key (reportId, fileName),
    foreign key (reportId) references BugReport(reportId)
);

insert into FunctionalArea values('User Interface');
insert into FunctionalArea values('Back-end');
insert into FunctionalArea values('Software');

insert into Employee values(null,'Tony Martinez', 'tony','password', 1, 'Software');
insert into Employee values(null, 'Archer Mill','archer','password', 2,  'Software');
insert into Employee values(null,'Jessica Martinez', 'jess','password', 1, 'Software');
insert into Employee values(null, 'John House','john','password', 2,  'Software');


insert into Program values(null,'Space Fighter', '1','1','Galactic Fighter');
insert into Program values(null,'Street Fighter', '1','1','2d console fighter');

insert into BugReport values(null,1,1,1,"summary",true,"test dat","fix nothing",1,'1990-1-1',2,"no comments",1,1,1,111,2,'1990-1-1',1,'1990-1-1',false);
    

