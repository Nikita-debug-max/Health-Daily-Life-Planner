
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

from database import get_db_connection

auth_bp = Blueprint("auth", __name__)


# 1. User registration
@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required."
        }), 400

    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({
            "error": "Please enter a valid email address."
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters long."
        }), 400

    password_hash = generate_password_hash(password)
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (name, email, password_hash)
        )
        conn.commit()

        return jsonify({
            "message": "Registration successful!",
            "user": {
                "id": cursor.lastrowid,
                "name": name,
                "email": email
            }
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "This email is already registered."
        }), 409

    finally:
        conn.close()


# 2. User login
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required."
        }), 400

    conn = get_db_connection()

    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()
    finally:
        conn.close()

    if user is None or not check_password_hash(
        user["password_hash"], password
    ):
        return jsonify({
            "error": "Invalid email or password."
        }), 401

    session.clear()
    session["user_id"] = user["id"]

    return jsonify({
        "message": "Login successful!",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200


# 3. User logout
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "message": "Logged out successfully."
    }), 200


# 4. Check the currently logged-in user
@auth_bp.route("/api/me", methods=["GET"])
def current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({
            "error": "Please log in first."
        }), 401

    conn = get_db_connection()

    try:
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    finally:
        conn.close()

    if user is None:
        session.clear()
        return jsonify({
            "error": "User not found. Please log in again."
        }), 401

    return jsonify({
        "user": dict(user)
    }), 200
