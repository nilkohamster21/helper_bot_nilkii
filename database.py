import sqlite3


def init_db():
    # создание таблицы
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            title TEXT
        )
    ''')
    conn.commit()

# функция для сохранения пользователя
def save_user(user):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, first_name, last_name, username)
        VALUES (?, ?, ?, ?)
    ''', (user.id, user.first_name, user.last_name, user.username))
    conn.commit()
    conn.close()

def save_in_bd_presentation_title(user_id, title):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO presentations (user_id, title) VALUES (?, ?)", (user_id, title))
    conn.commit()
    conn.close()


def get_presentations_by_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, timestamp FROM presentations
        WHERE user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
