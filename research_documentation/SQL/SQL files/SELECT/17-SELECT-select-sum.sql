# SELECT - Aggregate function (SUM)
# Selecting the joined information from tables employees and salaries for the employee with ID=10001. 
# This represent the union of both sets (inner join). We specify from which table the returned columns will be taken. 
# The query returns the total sum that employee with ID=10001 obtained.

SELECT employees.emp_no, 
	   employees.first_name, 
	   employees.last_name, 
       SUM(salaries.salary)
       
FROM employees INNER JOIN salaries 
	ON employees.emp_no=salaries.emp_no 
    
WHERE employees.emp_no='10001'