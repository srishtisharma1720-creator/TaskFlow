
import os
import sqlite3
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, g
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY", "local-development-key-change-before-deployment"
)

DATABASE = os.path.join(app.root_path, "database.db")


# ---------------- DATABASE ----------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)

    db.execute("PRAGMA foreign_keys = ON")

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Medium',
            due_date TEXT,
            status TEXT DEFAULT 'To Do'
        )
    """)

    # Upgrade an existing tasks table without deleting old data
    columns = {
        row[1] for row in db.execute(
            "PRAGMA table_info(tasks)"
        ).fetchall()
    }

    if "user_id" not in columns:
        db.execute(
            "ALTER TABLE tasks ADD COLUMN user_id INTEGER REFERENCES users(id)"
        )

    if "created_at" not in columns:
        db.execute(
            "ALTER TABLE tasks ADD COLUMN created_at TEXT"
        )

    db.commit()
    db.close()


# Initialize the schema both for direct runs and when this module is imported
# by a WSGI server or a test runner.
init_db()


# ---------------- AUTHENTICATION ----------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or len(password) < 8:
            flash("Enter all details. Password must be at least 8 characters.", "error")
            return redirect(url_for("register"))

        db = get_db()

        try:
            db.execute("""
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            """, (
                username,
                email,
                generate_password_hash(password)
            ))
            db.commit()

            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("This email is already registered.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()

        user = db.execute("""
            SELECT * FROM users WHERE email = ?
        """, (email,)).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Welcome to TaskFlow!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("login"))


# ---------------- DASHBOARD ----------------

@app.route("/")
@login_required
def dashboard():

    db = get_db()
    user_id = session["user_id"]

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")

    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if status in ["To Do", "In Progress", "Review", "Completed"]:
        query += " AND status = ?"
        params.append(status)

    if priority in ["Low", "Medium", "High"]:
        query += " AND priority = ?"
        params.append(priority)

    query += """
        ORDER BY
        CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END,
        due_date ASC,
        id DESC
    """

    tasks = db.execute(query, params).fetchall()

    counts = db.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN status = 'To Do' THEN 1 ELSE 0 END) AS todo,
            SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) AS progress,
            SUM(CASE WHEN status = 'Review' THEN 1 ELSE 0 END) AS review,
            SUM(CASE
                WHEN due_date < date('now')
                AND due_date != ''
                AND status != 'Completed'
                THEN 1 ELSE 0
            END) AS overdue
        FROM tasks WHERE user_id = ?
    """, (user_id,)).fetchone()

    total = counts["total"] or 0
    completed = counts["completed"] or 0
    completion_rate = round(completed / total * 100) if total else 0

    return render_template(
        "dashboard.html",
        tasks=tasks,
        counts=counts,
        completion_rate=completion_rate,
        search=search,
        selected_status=status,
        selected_priority=priority
    )


# ---------------- ADD TASK ----------------

@app.route("/add", methods=["POST"])
@login_required
def add_task():

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")
    status = request.form.get("status", "To Do")

    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for("dashboard"))

    if len(title) > 150:
        flash("Task title must be 150 characters or fewer.", "error")
        return redirect(url_for("dashboard"))

    if priority not in ["Low", "Medium", "High"]:
        flash("Invalid priority.", "error")
        return redirect(url_for("dashboard"))

    if status not in ["To Do", "In Progress", "Review", "Completed"]:
        flash("Invalid task status.", "error")
        return redirect(url_for("dashboard"))

    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            flash("Invalid deadline.", "error")
            return redirect(url_for("dashboard"))

    db = get_db()

    db.execute("""
        INSERT INTO tasks
        (title, description, priority, due_date, status, user_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        title, description, priority, due_date,
        status, session["user_id"]
    ))

    db.commit()

    flash("Task added successfully!", "success")
    return redirect(url_for("dashboard"))


# ---------------- EDIT TASK ----------------

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):

    db = get_db()
    user_id = session["user_id"]

    task = db.execute("""
        SELECT * FROM tasks
        WHERE id = ? AND user_id = ?
    """, (task_id, user_id)).fetchone()

    if task is None:
        return "Task not found", 404

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date", "")
        status = request.form.get("status", "To Do")

        if not title:
            flash("Title is required.", "error")
            return redirect(url_for("edit_task", task_id=task_id))

        if len(title) > 150:
            flash("Title must be 150 characters or fewer.", "error")
            return redirect(url_for("edit_task", task_id=task_id))

        if priority not in ["Low", "Medium", "High"]:
            flash("Invalid priority.", "error")
            return redirect(url_for("edit_task", task_id=task_id))

        if status not in ["To Do", "In Progress", "Review", "Completed"]:
            flash("Invalid status.", "error")
            return redirect(url_for("edit_task", task_id=task_id))

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                flash("Invalid deadline.", "error")
                return redirect(url_for("edit_task", task_id=task_id))

        db.execute("""
            UPDATE tasks
            SET title = ?, description = ?, priority = ?,
                due_date = ?, status = ?
            WHERE id = ? AND user_id = ?
        """, (
            title, description, priority,
            due_date, status, task_id, user_id
        ))

        db.commit()

        flash("Task updated successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit.html", task=task)


# ---------------- DELETE TASK ----------------

@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):

    db = get_db()

    db.execute("""
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
    """, (task_id, session["user_id"]))

    db.commit()

    flash("Task deleted.", "success")
    return redirect(url_for("dashboard"))


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)
