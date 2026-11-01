
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn



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

    # Check and update existing projects table
    project_columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(projects)"
        ).fetchall()
    ]

    if "description" not in project_columns:
        conn.execute(
            "ALTER TABLE projects ADD COLUMN description TEXT"
        )

    if "start_date" not in project_columns:
        conn.execute(
            "ALTER TABLE projects ADD COLUMN start_date TEXT"
        )

    if "end_date" not in project_columns:
        conn.execute(
            "ALTER TABLE projects ADD COLUMN end_date TEXT"
        )

    if "status" not in project_columns:
        conn.execute(
            "ALTER TABLE projects ADD COLUMN status TEXT NOT NULL DEFAULT 'Planned'"
        )

    # Check and update existing tasks table
    task_columns = [
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(tasks)"
        ).fetchall()
    ]

    if "task_name" not in task_columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN task_name TEXT"
        )

    if "project_id" not in task_columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN project_id INTEGER"
        )

    if "emp_id" not in task_columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN emp_id INTEGER"
        )

    if "due_date" not in task_columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN due_date TEXT"
        )

    if "priority" not in task_columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'Medium'"
        )

    if "status" not in task_columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN status TEXT NOT NULL DEFAULT 'Pending'"
        )

    if "description" not in task_columns:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN description TEXT"
        )

    conn.commit()
    conn.close()


@app.route("/")
def dashboard():
    conn = get_db()

    employees = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    departments = conn.execute(
        "SELECT COUNT(*) FROM departments"
    ).fetchone()[0]

    projects = conn.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0] if conn.execute(
        "SELECT COUNT(*) FROM sqlite_master "
        "WHERE type='table' AND name='projects'"
    ).fetchone()[0] else 0

    tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0] if conn.execute(
        "SELECT COUNT(*) FROM sqlite_master "
        "WHERE type='table' AND name='tasks'"
    ).fetchone()[0] else 0

    conn.close()

    return render_template(
        "index.html",
        total_employees=employees,
        total_departments=departments,
        total_projects=projects,
        total_tasks=tasks
    )


@app.route("/employees")
def employees():
    conn = get_db()

    employee_list = conn.execute("""
        SELECT e.*, d.dept_name
        FROM employees e
        LEFT JOIN departments d
        ON e.dept_id = d.dept_id
        ORDER BY e.emp_id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "employee/employee.html",
        employees=employee_list
    )


@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    conn = get_db()

    departments = conn.execute(
        "SELECT * FROM departments ORDER BY dept_name"
    ).fetchall()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip() or None
        phone = request.form.get("phone", "").strip()
        hire_date = request.form.get("hire_date", "")
        job_title = request.form.get("job_title", "").strip()
        salary_text = request.form.get("salary", "").strip()
        dept_id = request.form.get("dept_id", "")

        if not name:
            flash("Employee name is required.", "error")
            conn.close()
            return redirect(url_for("employee/add_employee"))

        try:
            salary = float(salary_text) if salary_text else None
            if salary is not None and salary < 0:
                raise ValueError
            dept_id = int(dept_id) if dept_id else None
        except ValueError:
            flash("Enter a valid salary and department.", "error")
            conn.close()
            return redirect(url_for("employee/add_employee"))

        try:
            conn.execute("""
                INSERT INTO employees
                (name, email, phone, hire_date,
                 job_title, salary, dept_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name, email, phone, hire_date,
                job_title, salary, dept_id
            ))

            conn.commit()
            flash("Employee added successfully!", "success")
            conn.close()
            return redirect(url_for("employee"))

        except sqlite3.IntegrityError:
            flash("This email already exists or the department is invalid.",
                  "error")

    conn.close()

    return render_template(
        "employee/add_employee.html",
        departments=departments
    )


@app.route("/employees/edit/<int:emp_id>",
           methods=["GET", "POST"])
def edit_employee(emp_id):
    conn = get_db()

    employee = conn.execute(
        "SELECT * FROM employees WHERE emp_id = ?",
        (emp_id,)
    ).fetchone()

    if employee is None:
        conn.close()
        flash("Employee not found.", "error")
        return redirect(url_for("employees"))

    departments = conn.execute(
        "SELECT * FROM departments ORDER BY dept_name"
    ).fetchall()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip() or None
        phone = request.form.get("phone", "").strip()
        hire_date = request.form.get("hire_date", "")
        job_title = request.form.get("job_title", "").strip()
        salary_text = request.form.get("salary", "").strip()
        dept_id = request.form.get("dept_id", "")

        if not name:
            flash("Employee name is required.", "error")
            conn.close()
            return redirect(url_for("edit_employee", emp_id=emp_id))

        try:
            salary = float(salary_text) if salary_text else None
            if salary is not None and salary < 0:
                raise ValueError
            dept_id = int(dept_id) if dept_id else None
        except ValueError:
            flash("Enter a valid salary and department.", "error")
            conn.close()
            return redirect(url_for("employee/edit_employee", emp_id=emp_id))

        try:
            conn.execute("""
                UPDATE employees
                SET name = ?, email = ?, phone = ?,
                    hire_date = ?, job_title = ?,
                    salary = ?, dept_id = ?
                WHERE emp_id = ?
            """, (
                name, email, phone, hire_date,
                job_title, salary, dept_id, emp_id
            ))

            conn.commit()
            flash("Employee updated successfully!", "success")
            conn.close()
            return redirect(url_for("employees"))

        except sqlite3.IntegrityError:
            flash("This email already exists or the department is invalid.",
                  "error")

    conn.close()

    return render_template(
        "employee/edit_employee.html",
        employee=employee,
        departments=departments
    )


@app.route("/employees/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):
    conn = get_db()

    employee = conn.execute(
        "SELECT emp_id FROM employees WHERE emp_id = ?",
        (emp_id,)
    ).fetchone()

    if employee is None:
        flash("Employee not found.", "error")
    else:
        conn.execute(
            "DELETE FROM employees WHERE emp_id = ?",
            (emp_id,)
        )
        conn.commit()
        flash("Employee deleted successfully!", "success")

    conn.close()
    return redirect(url_for("employees"))



@app.route("/departments")
def department_list():
    conn = get_db()

    departments = conn.execute("""
        SELECT d.*,
               COUNT(e.emp_id) AS employee_count
        FROM departments d
        LEFT JOIN employees e
            ON d.dept_id = e.dept_id
        GROUP BY d.dept_id
        ORDER BY d.dept_id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "department/departments.html",
        departments=departments
    )


@app.route("/departments/add", methods=["GET", "POST"])
def add_department():
    if request.method == "POST":
        dept_name = request.form.get(
            "dept_name", ""
        ).strip()

        location = request.form.get(
            "location", ""
        ).strip()

        if not dept_name:
            flash("Department name is required.", "error")
            return redirect(url_for("department/add_department"))

        conn = get_db()

        try:
            conn.execute("""
                INSERT INTO departments (dept_name, location)
                VALUES (?, ?)
            """, (dept_name, location))

            conn.commit()
            flash("Department added successfully!", "success")

        except sqlite3.IntegrityError:
            flash("This department name already exists.", "error")

        finally:
            conn.close()

        return redirect(url_for("department_list"))

    return render_template("department/add_department.html")


@app.route("/departments/edit/<int:dept_id>",
           methods=["GET", "POST"])
def edit_department(dept_id):
    conn = get_db()

    department = conn.execute(
        "SELECT * FROM departments WHERE dept_id = ?",
        (dept_id,)
    ).fetchone()

    if department is None:
        conn.close()
        flash("Department not found.", "error")
        return redirect(url_for("department/department_list"))

    if request.method == "POST":
        dept_name = request.form.get(
            "dept_name", ""
        ).strip()

        location = request.form.get(
            "location", ""
        ).strip()

        if not dept_name:
            conn.close()
            flash("Department name is required.", "error")
            return redirect(
                url_for("department/edit_department", dept_id=dept_id)
            )

        try:
            conn.execute("""
                UPDATE departments
                SET dept_name = ?, location = ?
                WHERE dept_id = ?
            """, (dept_name, location, dept_id))

            conn.commit()
            flash("Department updated successfully!", "success")

        except sqlite3.IntegrityError:
            flash("This department name already exists.", "error")

        finally:
            conn.close()

        return redirect(url_for("department_list"))

    conn.close()

    return render_template(
        "department/edit_department.html",
        department=department
    )


@app.route("/departments/delete/<int:dept_id>",
           methods=["POST"])
def delete_department(dept_id):
    conn = get_db()

    department = conn.execute(
        "SELECT dept_id FROM departments WHERE dept_id = ?",
        (dept_id,)
    ).fetchone()

    if department is None:
        flash("Department not found.", "error")
    else:
        conn.execute(
            "DELETE FROM departments WHERE dept_id = ?",
            (dept_id,)
        )
        conn.commit()
        flash(
            "Department deleted. Its employees remain "
            "saved without a department.",
            "success"
        )

    conn.close()
    return redirect(url_for("department_list"))



# ================= PROJECT MANAGEMENT =================

PROJECT_STATUSES = [
    "Planned",
    "In Progress",
    "Completed",
    "On Hold"
]


# PROJECT LIST

@app.route("/projects")
def projects():
    conn = get_db()

    project_list = conn.execute("""
        SELECT p.*,
               GROUP_CONCAT(e.name, ', ') AS assigned_employees
        FROM projects p
        LEFT JOIN project_assignments pa
            ON p.project_id = pa.project_id
        LEFT JOIN employees e
            ON pa.emp_id = e.emp_id
        GROUP BY p.project_id
        ORDER BY p.project_id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "projects/projects.html",
        projects=project_list
    )



# ADD PROJECT
@app.route("/projects/add", methods=["GET", "POST"])
def add_project():
    conn = get_db()

    if request.method == "POST":
        project_name = request.form.get("project_name", "").strip()
        description = request.form.get("description", "").strip()
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None
        status = request.form.get("status", "Planned")
        employee_ids = request.form.getlist("employees")

        if not project_name:
            conn.close()
            flash("Project name is required.", "danger")
            return redirect(url_for("projects/add_project"))

        if status not in PROJECT_STATUSES:
            conn.close()
            flash("Invalid project status.", "danger")
            return redirect(url_for("projects/add_project"))

        if start_date and end_date and end_date < start_date:
            conn.close()
            flash("End date cannot be before start date.", "danger")
            return redirect(url_for("add_project"))

        try:
            employee_ids = list(set(map(int, employee_ids)))

            if employee_ids:
                placeholders = ",".join("?" for _ in employee_ids)
                valid_ids = conn.execute(
                    f"SELECT emp_id FROM employees "
                    f"WHERE emp_id IN ({placeholders})",
                    employee_ids
                ).fetchall()

                if len(valid_ids) != len(employee_ids):
                    raise ValueError("Invalid employee selection.")

            cursor = conn.execute("""
                INSERT INTO projects
                (project_name, description, start_date, end_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                project_name, description,
                start_date, end_date, status
            ))

            project_id = cursor.lastrowid

            for emp_id in employee_ids:
                conn.execute("""
                    INSERT INTO project_assignments (project_id, emp_id)
                    VALUES (?, ?)
                """, (project_id, emp_id))

            conn.commit()
            flash("Project added successfully.", "success")
            conn.close()
            return redirect(url_for("projects"))

        except (ValueError, sqlite3.Error) as error:
            conn.rollback()
            conn.close()
            flash(f"Unable to add project: {error}", "danger")
            return redirect(url_for("add_project"))

    employees = conn.execute("""
        SELECT emp_id, name FROM employees ORDER BY name
    """).fetchall()

    conn.close()

    return render_template(
        "projects/add_projects.html",
        employees=employees
    )


# EDIT PROJECT
@app.route("/projects/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    conn = get_db()

    project = conn.execute(
        "SELECT * FROM projects WHERE project_id = ?",
        (project_id,)
    ).fetchone()

    if project is None:
        conn.close()
        flash("Project not found.", "danger")
        return redirect(url_for("projects"))

    if request.method == "POST":
        project_name = request.form.get("project_name", "").strip()
        description = request.form.get("description", "").strip()
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None
        status = request.form.get("status", "Planned")
        employee_ids = request.form.getlist("employees")

        if not project_name:
            conn.close()
            flash("Project name is required.", "danger")
            return redirect(url_for("projects/edit_projects", project_id=project_id))

        if status not in PROJECT_STATUSES:
            conn.close()
            flash("Invalid project status.", "danger")
            return redirect(url_for("projects/edit_projects", project_id=project_id))

        if start_date and end_date and end_date < start_date:
            conn.close()
            flash("End date cannot be before start date.", "danger")
            return redirect(url_for("projects/edit_projects", project_id=project_id))

        try:
            employee_ids = list(set(map(int, employee_ids)))

            if employee_ids:
                placeholders = ",".join("?" for _ in employee_ids)
                valid_ids = conn.execute(
                    f"SELECT emp_id FROM employees "
                    f"WHERE emp_id IN ({placeholders})",
                    employee_ids
                ).fetchall()

                if len(valid_ids) != len(employee_ids):
                    raise ValueError("Invalid employee selection.")

            conn.execute("""
                UPDATE projects
                SET project_name = ?, description = ?,
                    start_date = ?, end_date = ?, status = ?
                WHERE project_id = ?
            """, (
                project_name, description, start_date,
                end_date, status, project_id
            ))

            conn.execute(
                "DELETE FROM project_assignments WHERE project_id = ?",
                (project_id,)
            )

            for emp_id in employee_ids:
                conn.execute("""
                    INSERT INTO project_assignments (project_id, emp_id)
                    VALUES (?, ?)
                """, (project_id, emp_id))

            conn.commit()
            flash("Project updated successfully.", "success")
            conn.close()
            return redirect(url_for("projects"))

        except (ValueError, sqlite3.Error) as error:
            conn.rollback()
            conn.close()
            flash(f"Unable to update project: {error}", "danger")
            return redirect(url_for("projects/edit_projects", project_id=project_id))

    employees = conn.execute("""
        SELECT emp_id, name FROM employees ORDER BY name
    """).fetchall()

    assigned_employee_ids = {
        row["emp_id"] for row in conn.execute("""
            SELECT emp_id FROM project_assignments
            WHERE project_id = ?
        """, (project_id,)).fetchall()
    }

    conn.close()

    return render_template(
        "projects/edit_projects.html",
        project=project,
        employees=employees,
        assigned_employee_ids=assigned_employee_ids
    )


# DELETE PROJECT
@app.route("/projects/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM projects WHERE project_id = ?",
        (project_id,)
    )

    conn.commit()
    conn.close()

    flash("Project deleted successfully.", "success")
    return redirect(url_for("projects"))

# =========================
# TASK MANAGEMENT
# =========================

@app.route("/tasks")
def tasks():
    conn = get_db()

    task_list = conn.execute("""
        SELECT
            t.*,
            p.project_name,
            e.name AS employee_name
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.project_id
        LEFT JOIN employees e ON t.emp_id = e.emp_id
        ORDER BY t.task_id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "tasks/tasks.html",
        tasks=task_list
    )


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    conn = get_db()

    if request.method == "POST":
        task_name = request.form.get("task_name", "").strip()
        description = request.form.get("description", "").strip()
        project_id = request.form.get("project_id") or None
        emp_id = request.form.get("emp_id") or None
        due_date = request.form.get("due_date") or None
        priority = request.form.get("priority", "Medium")
        status = request.form.get("status", "Pending")

        if not task_name:
            projects = conn.execute(
                "SELECT project_id, project_name FROM projects"
            ).fetchall()
            employees = conn.execute(
                "SELECT emp_id, name FROM employees"
            ).fetchall()
            conn.close()

            flash("Task name is required.", "danger")
            return render_template(
                "tasks/add_tasks.html",
                projects=projects,
                employees=employees
            )

        conn.execute("""
            INSERT INTO tasks
            (task_name, description, project_id, emp_id,
             due_date, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task_name, description, project_id, emp_id,
            due_date, priority, status
        ))

        conn.commit()
        conn.close()

        flash("Task added successfully!", "success")
        return redirect(url_for("tasks"))

    projects = conn.execute(
        "SELECT project_id, project_name FROM projects"
    ).fetchall()

    employees = conn.execute(
        "SELECT emp_id, name FROM employees"
    ).fetchall()

    conn.close()

    return render_template(
        "tasks/add_tasks.html",
        projects=projects,
        employees=employees
    )


@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    conn = get_db()

    task = conn.execute(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        flash("Task not found.", "danger")
        return redirect(url_for("tasks"))

    if request.method == "POST":
        task_name = request.form.get("task_name", "").strip()
        description = request.form.get("description", "").strip()
        project_id = request.form.get("project_id") or None
        emp_id = request.form.get("emp_id") or None
        due_date = request.form.get("due_date") or None
        priority = request.form.get("priority", "Medium")
        status = request.form.get("status", "Pending")

        if not task_name:
            projects = conn.execute(
                "SELECT project_id, project_name FROM projects"
            ).fetchall()
            employees = conn.execute(
                "SELECT emp_id, name FROM employees"
            ).fetchall()
            conn.close()

            flash("Task name is required.", "danger")
            return render_template(
                "tasks/edit_tasks.html",
                task=task,
                projects=projects,
                employees=employees
            )

        conn.execute("""
            UPDATE tasks
            SET task_name = ?, description = ?, project_id = ?,
                emp_id = ?, due_date = ?, priority = ?, status = ?
            WHERE task_id = ?
        """, (
            task_name, description, project_id, emp_id,
            due_date, priority, status, task_id
        ))

        conn.commit()
        conn.close()

        flash("Task updated successfully!", "success")
        return redirect(url_for("tasks"))

    projects = conn.execute(
        "SELECT project_id, project_name FROM projects"
    ).fetchall()

    employees = conn.execute(
        "SELECT emp_id, name FROM employees"
    ).fetchall()

    conn.close()

    return render_template(
        "tasks/edit_tasks.html",
        task=task,
        projects=projects,
        employees=employees
    )


@app.route("/tasks/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM tasks WHERE task_id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    flash("Task deleted successfully!", "success")
    return redirect(url_for("tasks"))

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
