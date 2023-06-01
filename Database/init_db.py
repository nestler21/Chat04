import sqlite3


conn = sqlite3.connect("Chat_DB.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS users")
cur.execute("""
CREATE TABLE users (
    username      TEXT PRIMARY KEY
                        UNIQUE
                        NOT NULL,
    password TEXT NOT NULL
);
""")

cur.execute("DROP TABLE IF EXISTS sessions")
cur.execute("""
CREATE TABLE sessions (
    sid      TEXT PRIMARY KEY
                UNIQUE ON CONFLICT FAIL
                NOT NULL,
    username TEXT REFERENCES users (username) ON DELETE CASCADE
                UNIQUE ON CONFLICT REPLACE
                NOT NULL
);
""")

cur.execute("DROP TABLE IF EXISTS messages")
cur.execute("""
CREATE TABLE messages (
    mid      INTEGER PRIMARY KEY AUTOINCREMENT
                        NOT NULL
                        UNIQUE,
    sender   TEXT    REFERENCES users (username) ON DELETE SET NULL,
    receiver TEXT    REFERENCES users (username) ON DELETE SET NULL,
    message  TEXT,
    timestamp DATETIME
);
""")

conn.commit()
conn.close()