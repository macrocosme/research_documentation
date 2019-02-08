# DML - Adding a student to the Students table. 

# This case won't work as the DOB field is not specified (NOT NULL constraint). Uncomment line 9+ to run the correct code. 
INSERT INTO Students 
(ID,FirstName,LastName)
VALUES 
(1001,'John','Smith');

#INSERT INTO Students 
#(ID,FirstName,LastName,DOB)
#VALUES 
#(1001,'John','Smith','2000/1/1');
