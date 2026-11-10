import sqlite3

DB_NAME = "campusflow.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT,
            due_date TEXT,
            priority TEXT DEFAULT 'Medium',
            completed INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            duration REAL NOT NULL,
            study_date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            note TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            target TEXT,
            progress INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def fetch_data(table):
    allowed = {
        "tasks", "study_sessions",
        "expenses", "goals"
    }

    if table not in allowed:
        raise ValueError("Invalid table")

    conn = get_connection()
    rows = conn.execute(
        f"SELECT * FROM {table} ORDER BY id DESC"
    ).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def execute_query(sql, values=()):
    conn = get_connection()
    cursor = conn.execute(sql, values)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id