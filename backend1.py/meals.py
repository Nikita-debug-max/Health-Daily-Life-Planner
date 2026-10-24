
from datetime import date
from flask import Blueprint, request, jsonify, session

from database import get_db_connection

meals_bp = Blueprint("meals", __name__)

MEAL_TYPES = {"breakfast", "lunch", "dinner", "snack"}


# Create the meals table if it does not exist yet
def init_meals_table():
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                meal_name TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()


init_meals_table()


def logged_in_user():
    return session.get("user_id")


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


# 1. Add a meal
@meals_bp.route("/api/meals", methods=["POST"])
def add_meal():
    user_id = logged_in_user()
    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Send meal details as JSON."}), 400

    meal_type = data.get("meal_type")
    meal_name = data.get("meal_name")
    meal_date = data.get("meal_date", date.today().isoformat())
    notes = data.get("notes", "")

    if meal_type not in MEAL_TYPES:
        return jsonify({
            "error": "Meal type must be breakfast, lunch, dinner, or snack."
        }), 400

    if not isinstance(meal_name, str) or not meal_name.strip():
        return jsonify({"error": "Food name is required."}), 400

    if not valid_date(meal_date):
        return jsonify({"error": "Use meal_date format YYYY-MM-DD."}), 400

    if not isinstance(notes, str):
        return jsonify({"error": "Notes must be text."}), 400

    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            INSERT INTO meals
                (user_id, meal_date, meal_type, meal_name, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id, meal_date, meal_type,
            meal_name.strip(), notes.strip()
        ))
        conn.commit()

        meal = conn.execute("""
            SELECT * FROM meals
            WHERE id = ? AND user_id = ?
        """, (cursor.lastrowid, user_id)).fetchone()

        return jsonify(dict(meal)), 201
    finally:
        conn.close()


# 2. View meals (optionally filter by date)
@meals_bp.route("/api/meals", methods=["GET"])
def get_meals():
    user_id = logged_in_user()
    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    meal_date = request.args.get("date")
    if meal_date and not valid_date(meal_date):
        return jsonify({"error": "Use date format YYYY-MM-DD."}), 400

    conn = get_db_connection()
    try:
        if meal_date:
            rows = conn.execute("""
                SELECT * FROM meals
                WHERE user_id = ? AND meal_date = ?
                ORDER BY id
            """, (user_id, meal_date)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM meals
                WHERE user_id = ?
                ORDER BY meal_date DESC, id DESC
            """, (user_id,)).fetchall()

        return jsonify([dict(row) for row in rows]), 200
    finally:
        conn.close()


# 3. Edit a meal
@meals_bp.route("/api/meals/<int:meal_id>", methods=["PUT"])
def update_meal(meal_id):
    user_id = logged_in_user()
    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Send meal fields to update."}), 400

    allowed = {"meal_date", "meal_type", "meal_name", "notes"}
    if not set(data).issubset(allowed):
        return jsonify({"error": "Invalid meal fields."}), 400

    conn = get_db_connection()
    try:
        row = conn.execute("""
            SELECT * FROM meals WHERE id = ? AND user_id = ?
        """, (meal_id, user_id)).fetchone()

        if row is None:
            return jsonify({"error": "Meal not found."}), 404

        meal = dict(row)
        meal.update(data)

        if not valid_date(meal["meal_date"]):
            return jsonify({"error": "Use date format YYYY-MM-DD."}), 400

        if meal["meal_type"] not in MEAL_TYPES:
            return jsonify({"error": "Invalid meal type."}), 400

        if not isinstance(meal["meal_name"], str) or not meal["meal_name"].strip():
            return jsonify({"error": "Meal name is required."}), 400

        if not isinstance(meal["notes"], str):
            return jsonify({"error": "Notes must be text."}), 400

        conn.execute("""
            UPDATE meals
            SET meal_date = ?, meal_type = ?, meal_name = ?, notes = ?
            WHERE id = ? AND user_id = ?
        """, (
            meal["meal_date"], meal["meal_type"],
            meal["meal_name"].strip(), meal["notes"].strip(),
            meal_id, user_id
        ))
        conn.commit()

        updated = conn.execute("""
            SELECT * FROM meals WHERE id = ? AND user_id = ?
        """, (meal_id, user_id)).fetchone()

        return jsonify(dict(updated)), 200
    finally:
        conn.close()


# 4. Delete a meal
@meals_bp.route("/api/meals/<int:meal_id>", methods=["DELETE"])
def delete_meal(meal_id):
    user_id = logged_in_user()
    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    conn = get_db_connection()
    try:
        cursor = conn.execute("""
            DELETE FROM meals WHERE id = ? AND user_id = ?
        """, (meal_id, user_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Meal not found."}), 404

        return jsonify({"message": "Meal deleted successfully."}), 200
    finally:
        conn.close()
