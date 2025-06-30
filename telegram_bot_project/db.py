import sqlite3

DB_NAME = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            full_name TEXT,
            phone TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            file_id TEXT,
            caption TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            telegram_id INTEGER PRIMARY KEY
        )
    """)

    conn.commit()
    conn.close()

def add_user(telegram_id, full_name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (telegram_id, full_name) VALUES (?, ?)", (telegram_id, full_name))
    conn.commit()
    conn.close()

def update_user_phone(telegram_id, phone):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET phone = ? WHERE telegram_id = ?", (phone, telegram_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT telegram_id FROM users WHERE phone IS NOT NULL")
    users = cur.fetchall()
    conn.close()
    return [user[0] for user in users]

def save_post(post_type, file_id, caption):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO posts (type, file_id, caption) VALUES (?, ?, ?)", (post_type, file_id, caption))
    conn.commit()
    conn.close()

def get_all_posts():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    conn.close()
    return posts

def delete_post(post_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def is_admin(telegram_id):
    return telegram_id in [6394510301]
