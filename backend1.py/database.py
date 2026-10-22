
import sqlite3
from pathlib import Path

# Store the database in a dedicated folder
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "instance"
DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "health_planner.db"


# Connect to the database
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create all required tables
def init_db():
    conn = get_db_connection()

    try:
        # 1. Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Tasks table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT DEFAULT 'medium'
                    CHECK (priority IN ('low', 'medium', 'high')),
                is_completed INTEGER DEFAULT 0
                    CHECK (is_completed IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        # 3. Health records table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                record_date TEXT NOT NULL,
                water_ml INTEGER DEFAULT 0
                    CHECK (water_ml >= 0),
                sleep_hours REAL DEFAULT 0
                    CHECK (sleep_hours >= 0),
                exercise_minutes INTEGER DEFAULT 0
                    CHECK (exercise_minutes >= 0),
                steps INTEGER DEFAULT 0
                    CHECK (steps >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, record_date),
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        # 4. Meals table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_date TEXT NOT NULL,
                meal_type TEXT NOT NULL
                    CHECK (meal_type IN (
                        'breakfast', 'lunch', 'dinner', 'snack'
                    )),
                meal_name TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Database and tables created successfully!")

    finally:
        conn.close()


# Run this file directly to initialize the database
if __name__ == "__main__":
    init_db()
