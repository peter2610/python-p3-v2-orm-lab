# lib/employee.py
from __init__ import CURSOR, CONN
from department import Department

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Dept ID: {self.department_id}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and value.strip():
            self._name = value
        else:
            raise ValueError("Name must be a non-empty string")

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if isinstance(value, str) and value.strip():
            self._job_title = value
        else:
            raise ValueError("Job title must be a non-empty string")

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        if isinstance(value, int) and Department.find_by_id(value):
            self._department_id = value
        else:
            raise ValueError("department_id must reference an existing department")

    @classmethod
    def create_table(cls):
        sql = """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()

    def save(self):
        sql = "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        sql = "UPDATE employees SET name=?, job_title=?, department_id=? WHERE id=?"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM employees WHERE id=?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, job_title, department_id):
        emp = cls(name, job_title, department_id)
        emp.save()
        return emp

    @classmethod
    def instance_from_db(cls, row):
        emp = cls.all.get(row[0])
        if emp:
            emp.name = row[1]
            emp.job_title = row[2]
            emp.department_id = row[3]
        else:
            emp = cls(row[1], row[2], row[3], row[0])
            cls.all[emp.id] = emp
        return emp

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM employees").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute("SELECT * FROM employees WHERE name=?", (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def reviews(self):
        from review import Review
        sql = "SELECT * FROM reviews WHERE employee_id=?"
        CURSOR.execute(sql, (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]
