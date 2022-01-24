from employee_class import ZSqlite, Employee
from my_import_statements import *

class Employees(ZSqlite):
    def __init__(self, emp_list: list):
        """
        emp_list: a list of Employee objects
        """
        super().__init__(Employee.db_path)
        self.employees = emp_list

    @classmethod
    def all(cls):
        return cls([Employee(emp_tuple[0]) for emp_tuple in ZSqlite(Employee.db_path).exec_sql("SELECT ID FROM employees;", fetch_str="all")])

    def get_status(self, boolean):
        return [employee for employee in self.employees if employee.get_status() == boolean]





all_emps = Employees.all()
print(all_emps.employees)

