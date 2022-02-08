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

    def get_employees_based_on_status(self, status=True):
        return [employee for employee in self.employees if employee.get_status() == status]

    def get_employees_based_on_if_they_came_to_work(self, day: datetime, did_they_come=True):
        return [employee for employee in self.employees if employee.came_to_work_on(day) == did_they_come]







all_emps = Employees.all()
print(Employee("E1").came_to_work_on(datetime.strptime("1/24/2022", "%m/%d/%Y")))

