# DML - Updating (modifying) fields for a specific item (student with ID=1002). 
# 		Note that MySQL accepts the form `variable` to specify the column name instead of simply typing the variable
#		(e.g. `FirstName` instead of FirstName).

UPDATE Students
SET
`FirstName` = 'Caroline',
`LastName` = 'Herschel',
`DOB` = '2000/2/2'
WHERE `ID` = 1002;