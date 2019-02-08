# SELECT - Join
# Selecting the joined information from tables employees and salaries for the employee with ID=10001. 
# This represent the union of both sets (inner join). All columns from both tables are returned.

SELECT *
FROM employees INNER JOIN salaries 
	ON employees.emp_no=salaries.emp_no 
WHERE employees.emp_no='10001';