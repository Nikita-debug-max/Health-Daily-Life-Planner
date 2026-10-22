
from flask import Blueprint, request, jsonify, session
from datetime import date

from database import get_db_connection

health_bp = Blueprint("health", __name__)


# 1. Add or update today's health record
@health_bp.route("/api/health", methods=["POST"])
def save_health_record():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    data = request.get_json(silent=True) or {}

    record_date = data.get("record_date", date.today().isoformat())
    water_ml = data.get("water_ml", 0)
    sleep_hours = data.get("sleep_hours", 0)
    exercise_minutes = data.get("exercise_minutes", 0)
    steps = data.get("steps", 0)

    # Validate date
    try:
        date.fromisoformat(record_date)
    except (ValueError, TypeError):
        return jsonify({"error": "Use a valid date in YYYY-MM-DD format."}), 400

    # Validate numeric values (reject negative values and booleans)
    values = {
        "water_ml": water_ml,
        "sleep_hours": sleep_hours,
        "exercise_minutes": exercise_minutes,
        "steps": steps
    }

    for field, value in values.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return jsonify({"error": f"{field} must be a number."}), 400
        if value < 0:
            return jsonify({"error": f"{field} cannot be negative."}), 400

    if not isinstance(water_ml, int) or not isinstance(steps, int):
        return jsonify({
            "error": "water_ml and steps must be whole numbers."
        }), 400

    if not isinstance(exercise_minutes, int):
        return jsonify({
            "error": "exercise_minutes must be a whole number."
        }), 400

    if sleep_hours > 24 or exercise_minutes > 1440:
        return jsonify({
            "error": "Sleep or exercise duration exceeds one day."
        }), 400

    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO health_records
                (user_id, record_date, water_ml,
                 sleep_hours, exercise_minutes, steps)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, record_date) DO UPDATE SET
                water_ml = excluded.water_ml,
                sleep_hours = excluded.sleep_hours,
                exercise_minutes = excluded.exercise_minutes,
                steps = excluded.steps
            """,
            (
                user_id, record_date, water_ml,
                sleep_hours, exercise_minutes, steps
            )
        )
        conn.commit()

        row = conn.execute(
            """
            SELECT * FROM health_records
            WHERE user_id = ? AND record_date = ?
            """,
            (user_id, record_date)
        ).fetchone()

        return jsonify(dict(row)), 200

    finally:
        conn.close()


# 2. View health records
@health_bp.route("/api/health", methods=["GET"])
def get_health_records():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    conn = get_db_connection()

    try:
        rows = conn.execute(
            """
            SELECT * FROM health_records
            WHERE user_id = ?
            ORDER BY record_date DESC
            """,
            (user_id,)
        ).fetchall()

        return jsonify([dict(row) for row in rows]), 200

    finally:
        conn.close()


# 3. View one day's health record
@health_bp.route("/api/health/<record_date>", methods=["GET"])
def get_health_record(record_date):
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"error": "Please log in first."}), 401

    try:
        date.fromisoformat(record_date)
    except ValueError:
        return jsonify({"error": "Invalid date format."}), 400

    conn = get_db_connection()

    try:
        row = conn.execute(
            """
            SELECT * FROM health_records
            WHERE user_id = ? AND record_date = ?
            """,
            (user_id, record_date)
        ).fetchone()

        if row is None:
            return jsonify({"error": "No record found for this date."}), 404

        return jsonify(dict(row)), 200

    finally:
        conn.close()
