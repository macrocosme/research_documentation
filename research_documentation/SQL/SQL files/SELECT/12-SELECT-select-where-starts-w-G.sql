# SELECT - WHERE clause (logical operator AND), wildcard.
# Selecting all employees of female gender with first name starting with the letter 'G' followed by any other string (wildcard %). 
# Note that we do not say first_name = <condition> but first_name LIKE. LIKE is a string operator that compares character by character.
# Returning all columns from the employees table (*).

SELECT * 
FROM employees 
WHERE gender='F' AND first_name LIKE 'G%';