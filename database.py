import sqlite3
import os

# Database file path
DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database.db"
)


# Database Connection
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create Database Tables
def create_tables():
    conn = get_db()

    conn.executescript("""
    
    CREATE TABLE IF NOT EXISTS departments (
        dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
        dept_name TEXT NOT NULL UNIQUE,
        location TEXT
    );

    CREATE TABLE IF NOT EXISTS employees (
        emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        hire_date TEXT,
        job_title TEXT,
        salary REAL,
        dept_id INTEGER,
        FOREIGN KEY (dept_id)
            REFERENCES departments(dept_id)
            ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS projects (
        project_id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_name TEXT NOT NULL,
        description TEXT,
        start_date TEXT,
        end_date TEXT,
        status TEXT NOT NULL DEFAULT 'Planned'
    );

    CREATE TABLE IF NOT EXISTS project_assignments (
        project_id INTEGER NOT NULL,
        emp_id INTEGER NOT NULL,
        PRIMARY KEY (project_id, emp_id),
        FOREIGN KEY (project_id)
            REFERENCES projects(project_id)
            ON DELETE CASCADE,
        FOREIGN KEY (emp_id)
            REFERENCES employees(emp_id)
            ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        description TEXT,
        project_id INTEGER,
        emp_id INTEGER,
        due_date TEXT,
        priority TEXT NOT NULL DEFAULT 'Medium',
        status TEXT NOT NULL DEFAULT 'Pending',
        FOREIGN KEY (project_id)
            REFERENCES projects(project_id)
            ON DELETE SET NULL,
        FOREIGN KEY (emp_id)
            REFERENCES employees(emp_id)
            ON DELETE SET NULL
    );

    """)

    
    conn.close()
