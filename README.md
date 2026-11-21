# TaskFlow – Smart Task Management Web Application

TaskFlow is a task management web application developed using Python, Flask, SQLite, HTML, CSS, and JavaScript. It helps users organise their daily work, manage deadlines, track task progress, and stay productive through a simple dashboard.

## Features

- **User Authentication:** Register, log in, and log out securely.
- **Task Management:** Create, view, edit, and delete tasks.
- **Task Priorities:** Organise tasks according to priority.
- **Task Status:** Track tasks as To Do, In Progress, Review, or Completed.
- **Deadline Management:** Set deadlines for tasks.
- **Search and Filters:** Find tasks and filter them by status or priority.
- **Dashboard:** View task statistics and completion progress.
- **Theme Switching:** Switch between dark and light themes.
- **Responsive Interface:** Use the application on different screen sizes.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Page structure |
| CSS3 | Styling and responsive design |
| JavaScript | Frontend interactions |
| Werkzeug | Password hashing utilities |

## Project Structure

```text
TaskFlow/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── edit.html
│   ├── login.html
│   └── register.html
│   
└── static/
    ├── style.css
    └── script.js
```

The SQLite database is created by the application when required.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/TaskFlow.git
```

### 2. Open the project folder

```bash
cd TaskFlow
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

Open this address in your browser:

```text
http://127.0.0.1:5000
```

## Database

TaskFlow uses SQLite to store user and task information. The database is created automatically by the application.

## Security Notes

- Passwords are stored using password hashing.
- User sessions are used for authentication.
- Users should only be able to manage their own tasks.
- Production deployment should use a strong secret key stored in environment variables.
- CSRF protection, secure cookie settings, and appropriate input validation should be configured before public production use.

## Future Improvements

- Add task reminders and notifications.
- Add task sorting and calendar view.
- Add charts for productivity analysis.
- Add password reset functionality.
- Add automated tests.
- Add a persistent production database.

## Author
 
 Srishti Sharma

Developed as a personal portfolio project to practise Python, Flask, database management, and frontend development.
