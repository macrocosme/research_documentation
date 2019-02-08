# SELECT - WHERE clause (logical operator AND)
# Select employees born between 1st January 1963 (inclusively) and 1st January 1964 (exclusively).

SELECT * 
FROM employees 
WHERE birth_date>='1963-1-1' 
	AND birth_date<'1964-1-1';