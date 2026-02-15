import sqlite3

def get_connection():
    return sqlite3.connect("game.db")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        name TEXT,
        gender TEXT,
        age INTEGER,
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        hp INTEGER DEFAULT 100,
        max_hp INTEGER DEFAULT 100,
        attack INTEGER DEFAULT 10,
        defense INTEGER DEFAULT 5,
        energy INTEGER DEFAULT 100,
        max_energy INTEGER DEFAULT 100,
        silver INTEGER DEFAULT 0,
        cases INTEGER DEFAULT 5,
        last_case_time INTEGER DEFAULT 0,
        rating INTEGER DEFAULT 0,
        hidden INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
