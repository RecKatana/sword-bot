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
    # ===== Таблица заявок в друзья =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS friend_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_user INTEGER,
        to_user INTEGER
    )
    """)

    # ===== Таблица друзей =====
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS friends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1 INTEGER,
        user2 INTEGER
    )
    """)

def send_friend_request(from_user, to_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO friend_requests (from_user, to_user) VALUES (?, ?)",
        (from_user, to_user)
    )
    conn.commit()
    conn.close()


def get_friend_request(from_user, to_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM friend_requests WHERE from_user = ? AND to_user = ?",
        (from_user, to_user)
    )
    request = cursor.fetchone()
    conn.close()
    return request


def delete_friend_request(from_user, to_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM friend_requests WHERE from_user = ? AND to_user = ?",
        (from_user, to_user)
    )
    conn.commit()
    conn.close()

def add_friend(user1, user2):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO friends (user1, user2) VALUES (?, ?)",
        (user1, user2)
    )
    conn.commit()
    conn.close()


def get_friends(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT users.*
    FROM friends
    JOIN users ON users.tg_id = friends.user1 OR users.tg_id = friends.user2
    WHERE (friends.user1 = ? OR friends.user2 = ?)
    AND users.tg_id != ?
    """, (user_id, user_id, user_id))

    friends = cursor.fetchall()
    conn.close()
    return friends
   

# === Получить пользователя ===
def get_user(tg_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT name, level, exp, hp, max_hp, silver
    FROM users 
    WHERE tg_id=?
    """, (tg_id,))
    user = cursor.fetchone()

    conn.close()
    return user


# === Создать пользователя ===
def create_user(tg_id, name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO users (tg_id, name, gender, age)
    VALUES (?, ?, ?, ?)
    """, (tg_id, name, "Не указан", 18))

    conn.commit()
    conn.close()


# === Обновить серебро ===
def update_silver(tg_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET silver = silver + ?
    WHERE tg_id = ?
    """, (amount, tg_id))

    conn.commit()
    conn.close()
