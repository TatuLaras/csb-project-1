import sqlite3
import os

# Creates agents.sqlite
# TMC has issues with binary files, so we will go around by creating it locally from the text dump.

db = """
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    content TEXT NOT NULL
);
COMMIT;
"""

db_path = os.path.dirname(__file__) + "/csbproject1/db.sqlite"

if os.path.exists(db_path):
    print(f"{db_path} already exists")
else:
    conn = sqlite3.connect(db_path)
    conn.cursor().executescript(db)
    conn.commit()
