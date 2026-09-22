import os
import sqlite3


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(PROJECT_ROOT, "queries", "database.db")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "queries", "schema.sql")


def get_database_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_database_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())
    user_columns = connection.execute("PRAGMA table_info(users)").fetchall()
    if not any(column["name"] == "role" for column in user_columns):
        connection.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'student'")
    connection.commit()
    connection.close()
