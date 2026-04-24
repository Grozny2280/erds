import sqlite3
from datetime import datetime, timedelta

DB_NAME = "addiction_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            addiction_type TEXT,
            last_checkin TIMESTAMP,
            start_date TIMESTAMP,
            total_days_clean INTEGER,
            notifications_enabled INTEGER DEFAULT 1
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS relapse_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            relapse_date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def register_user(user_id, addiction_type):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now()
    c.execute('''
        INSERT OR REPLACE INTO users (user_id, addiction_type, last_checkin, start_date, total_days_clean)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, addiction_type, now, now, 0))
    conn.commit()
    conn.close()

def update_checkin(user_id, relapse=False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now()
    if relapse:
        c.execute("SELECT start_date, total_days_clean FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if row:
            clean_days = (datetime.now() - datetime.fromisoformat(row[0])).days
            new_total = row[1] + max(0, clean_days)  # добавляем дни до срыва
            c.execute('''
                UPDATE users SET start_date = ?, total_days_clean = ?, last_checkin = ? WHERE user_id = ?
            ''', (now, new_total, now, user_id))
            c.execute("INSERT INTO relapse_log (user_id, relapse_date) VALUES (?, ?)", (user_id, now))
    else:
        c.execute("UPDATE users SET last_checkin = ? WHERE user_id = ?", (now, user_id))
    conn.commit()
    conn.close()

def get_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT addiction_type, start_date, total_days_clean FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        return None
    addiction_type, start_date_str, total_clean = row
    start_date = datetime.fromisoformat(start_date_str)
    current_streak = (datetime.now() - start_date).days
    conn.close()
    return addiction_type, current_streak, total_clean

def toggle_notifications(user_id, enabled):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET notifications_enabled = ? WHERE user_id = ?", (1 if enabled else 0, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE notifications_enabled = 1")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users
