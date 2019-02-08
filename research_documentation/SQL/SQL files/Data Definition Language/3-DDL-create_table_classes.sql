# DDL - Create a new table called 'Classes' with fields ID, AcademicYear, and Class. 
# 		The primary key is the set to the joined columns ID and Academic Year.

CREATE TABLE Classes(
 ID INTEGER,
 AcademicYear INTEGER,
 Class VARCHAR(2),
 PRIMARY KEY (ID, AcademicYear)
);