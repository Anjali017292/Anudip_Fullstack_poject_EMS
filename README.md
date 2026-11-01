# Employee Management System (EMS)

## Project Overview

The **Employee Management System (EMS)** is a web-based application developed using Python Flask and SQLite. It provides a centralized platform to manage employee records, departments, projects, and tasks efficiently.

The system helps simplify organizational data management through structured interfaces and CRUD (Create, Read, Update, Delete) operations.

## Features

### 1. Employee Management
- View employee records
- Register new employees
- Update employee details
- Delete employee records

### 2. Department Management
- View department details
- Create new departments
- Edit department information
- Delete departments

### 3. Project Management
- View project records
- Create new projects
- Update project details
- Delete projects

### 4. Task Management
- View task details
- Create and assign tasks
- Update task information
- Delete tasks

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML5 | Web page structure |
| CSS3 | Styling and layout |
| JavaScript | Client-side functionality |

## Project Structure

```text
employee_management_system/
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/
    ├── base.html
    ├── index.html
    ├── employee/
    │   ├── employee.html
    │   ├── add_employee.html
    │   └── edit_employee.html
    │
    ├── department/
    │   ├── department.html
    │   ├── add_department.html
    │   └── edit_department.html
    │
    ├── project/
    │   ├── project.html
    │   ├── add_project.html
    │   └── edit_project.html
    │
    └── task/
        ├── task.html
        ├── add_task.html
        └── edit_task.html
```

## Installation and Setup

Follow these steps to run the project locally.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Anjali017292/Anudip_Fullstack_poject_EMS.git
```

### Step 2: Navigate to the Project Directory

```bash
cd Anudip_Fullstack_poject_EMS
```

### Step 3: Create a Virtual Environment

```bash
python -m venv env
```

### Step 4: Activate the Virtual Environment

For Windows:

```bash
env\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## Database

The application uses **SQLite** for storing and managing data. Database connectivity and database operations are handled through `database.py`.

## Learning Outcomes

- Practical experience with Python Flask
- Understanding of SQLite database connectivity
- Implementation of CRUD operations
- Working with HTML templates and routing
- Understanding of full-stack web application development

## Author

**Anjali Rathi**

GitHub: [Anjali017292](https://github.com/Anjali017292)

## Repository

[Employee Management System – GitHub](https://github.com/Anjali017292/Anudip_Fullstack_poject_EMS)

---

*Developed as part of Full Stack Development Training at Anudip Foundation.*
