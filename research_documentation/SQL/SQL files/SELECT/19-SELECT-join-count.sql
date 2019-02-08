# SELECT - GROUP BY
# 	     - Aggregate function (COUNT)	
# Counting the number of employee per department

SELECT departments.dept_name, COUNT(*) 
FROM dept_emp AS de INNER JOIN departments
	ON de.dept_no=departments.dept_no 
GROUP BY departments.dept_name