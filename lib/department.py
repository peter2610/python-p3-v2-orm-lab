# lib/department.py
from __init__ import CURSOR, CONN

class Department:
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str) and name.strip():
            self._name = name
        else:
            raise ValueError("Name must be a non-empty string")

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        if isinstance(location, str) and location.strip():
            self._location = location
        else:
            raise ValueError("Location must be a non-empty string")

    @classmethod
    def create_table(cls):
        sql = """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT
        )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CONN.commit()

    def save(self):
        sql = "INSERT INTO departments (name, location) VALUES (?, ?)"
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, location):
        dept = cls(name, location)
        dept.save()
        return dept

    def update(self):
        sql = "UPDATE departments SET name=?, location=? WHERE id=?"
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM departments WHERE id=?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        department = cls.all.get(row[0])
        if department:
            department.name = row[1]
            department.location = row[2]
        else:
            department = cls(row[1], row[2], row[0])
            cls.all[department.id] = department
        return department

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM departments").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM departments WHERE id=?", (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute("SELECT * FROM departments WHERE name=?", (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def employees(self):
        from employee import Employee
        rows = CURSOR.execute("SELECT * FROM employees WHERE department_id=?", (self.id,)).fetchall()
        return [Employee.instance_from_db(row) for row in rows]
