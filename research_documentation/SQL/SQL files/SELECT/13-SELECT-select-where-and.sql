# SELECT - WHERE clause (logical operator AND)
# Selecting female employess hired prior to 1st January 1988.  

SELECT * 
FROM employees 
WHERE gender='F' AND hire_date<'1988-1-1'; 