#AttachmentAttachmentdrop  
#drop table Attachment;
#drop table BugReport;
#drop table Program;
#drop table Employee;
#drop table FunctionalArea;

drop database bughound;
create database bughound;
use bughound;

create table Employee(
    employeeId int(10) not null auto_increment,
    name varchar(40) not null,
    username varchar(40) not null,
    password varchar(40) not null,
    level int(1) not null,
    primary key (employeeID)
);

create table Program(
    programId int(10) not null auto_increment,
    name varchar(40) not null,
    version int(3) not null,
    releaseNumber int(3) not null,
    description varchar(200) not null,
    primary key (programID)    
);

create table FunctionalArea(
	areaId int(10) not null auto_increment,
    areaName varchar(40) not null,
    programId int(10) not null,
    primary key (areaId),
    foreign key (programId) references Program(programId)
);


create table BugReport(
    reportId int(10) not null auto_increment,
    programId int(10) not null,
    reportType int(10) not null,
    severity int(5) not null,
    summary varchar(400) not null,
    reproducable boolean not null,
    description varchar(400) not null,
    suggestedFix varchar(400),
    reportedBy int(10) not null,
    discoveredDate date not null,
    assignedTo int(10),
    comments varchar(400),
    status int(1),
    priority int(1),
    resolution int(2),
    resolutionVersion int(3),
    resolvedBy int(10),
    resolvedDate date,
    testedBy int(10),
    testedDate date,
    deferred boolean,
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


insert into Employee values(null,'Tony Martinez', 'tony','password', 1);
insert into Employee values(null, 'Archer Mill','archer','password', 2);
insert into Employee values(null,'Jessica Martinez', 'jess','password', 1);
insert into Employee values(null, 'John House','john','password', 2);


insert into Program values(null,'Space Fighter', '1','1','Galactic Fighter');
insert into Program values(null,'Street Fighter', '1','1','2d console fighter');

insert into FunctionalArea values(null,'User Interface',1);
insert into FunctionalArea values(null,'Back-end',1);
insert into FunctionalArea values(null,'Software',1);

insert into BugReport values(null,1,1,1,"summary",true,"test dat","fix nothing",1,'1990-1-1',2,"no comments",1,1,1,111,2,'1990-1-1',1,'1990-1-1',false);
    
    
    
    
    
    
    
    
    
    
    

