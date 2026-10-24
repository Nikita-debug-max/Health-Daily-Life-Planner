
from flask import Blueprint, request, jsonify, session

from database import get_db_connection

tasks_bp = Blueprint("tasks", __name__)


# Helper: make sure the user is logged in
def get_logged_in_user():
    return session.get("user_id")


# 1. Add a new task
@tasks_bp.route("/api/tasks", methods=["POST"])
def add_task():
    user_id = get_logged_in_user()

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    data = request.get_json(silent=True) or {}

    title = data.get("title", "")
    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Task title is required."}), 400

    title = title.strip()
    description = data.get("description", "")
    due_date = data.get("due_date")
    priority = data.get("priority", "medium")

    if not isinstance(description, str):
        return jsonify({"error": "Description must be text."}), 400

    if due_date is not None and not isinstance(due_date, str):
        return jsonify({"error": "Due date must be text."}), 400

    if priority not in ("low", "medium", "high"):
        return jsonify({
            "error": "Priority must be low, medium, or high."
        }), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO tasks
            (user_id, title, description, due_date, priority)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, title, description.strip(), due_date, priority)
        )
        conn.commit()

        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (cursor.lastrowid, user_id)
        ).fetchone()

        return jsonify(dict(task)), 201
    finally:
        conn.close()


# 2. View all tasks belonging to the logged-in user
@tasks_bp.route("/api/tasks", methods=["GET"])
def get_tasks():
    user_id = get_logged_in_user()

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    conn = get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT * FROM tasks
            WHERE user_id = ?
            ORDER BY is_completed ASC, id DESC
            """,
            (user_id,)
        ).fetchall()

        return jsonify([dict(row) for row in rows]), 200
    finally:
        conn.close()


# 3. Update a task
@tasks_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    user_id = get_logged_in_user()

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    data = request.get_json(silent=True) or {}
    allowed_fields = {
        "title", "description", "due_date", "priority", "is_completed"
    }

    if not data or not set(data.keys()).issubset(allowed_fields):
        return jsonify({
            "error": "Provide valid task fields to update."
        }), 400

    conn = get_db_connection()
    try:
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        ).fetchone()

        if task is None:
            return jsonify({"error": "Task not found."}), 404

        updated = dict(task)

        for field, value in data.items():
            if field == "title":
                if not isinstance(value, str) or not value.strip():
                    return jsonify({
                        "error": "Title cannot be empty."
                    }), 400
                value = value.strip()

            elif field == "description":
                if not isinstance(value, str):
                    return jsonify({
                        "error": "Description must be text."
                    }), 400
                value = value.strip()

            elif field == "due_date":
                if value is not None and not isinstance(value, str):
                    return jsonify({
                        "error": "Due date must be text."
                    }), 400

            elif field == "priority":
                if value not in ("low", "medium", "high"):
                    return jsonify({
                        "error": "Priority must be low, medium, or high."
                    }), 400

            elif field == "is_completed":
                if value not in (0, 1, False, True):
                    return jsonify({
                        "error": "is_completed must be true or false."
                    }), 400
                value = int(value)

            updated[field] = value

        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?,
                priority = ?, is_completed = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                updated["title"],
                updated["description"],
                updated["due_date"],
                updated["priority"],
                updated["is_completed"],
                task_id,
                user_id
            )
        )
        conn.commit()

        result = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        ).fetchone()

        return jsonify(dict(result)), 200
    finally:
        conn.close()


# 4. Delete a task
@tasks_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    user_id = get_logged_in_user()

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found."}), 404

        return jsonify({
            "message": "Task deleted successfully."
        }), 200
    finally:
        conn.close()


# 5. Mark a task as completed
@tasks_bp.route(
    "/api/tasks/<int:task_id>/complete",
    methods=["PATCH"]
)
def complete_task(task_id):
    user_id = get_logged_in_user()

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    data = request.get_json(silent=True) or {}
    completed = data.get("is_completed", True)

    if not isinstance(completed, bool):
        return jsonify({
            "error": "is_completed must be true or false."
        }), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE tasks
            SET is_completed = ?
            WHERE id = ? AND user_id = ?
            """,
            (int(completed), task_id, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found."}), 404

        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        ).fetchone()

        return jsonify(dict(task)), 200
    finally:
        conn.close()
