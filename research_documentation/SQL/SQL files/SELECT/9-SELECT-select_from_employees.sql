# SELECT 
# USE specifies to set the database 'employees' as default. This will avoid us having to specify the database in our queries 
#															(e.g. FROM database_name.table_name, or FROM `database_name`.`table_name`) 
USE employees;

# DML - Selecting all columns from the employees table. As we do not specify any WHERE conditions, all rows will be returned.

SELECT emp_no, birth_date, first_name, last_name, gender,hire_date
FROM employees;
