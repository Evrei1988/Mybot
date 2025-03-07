import sqlite3

def init_db():
    """Создает таблицу, если её нет"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        wo_number TEXT,
                        sa_number TEXT,
                        time_start TEXT,
                        time_end TEXT,
                        pdf_path TEXT
                    )''')
    conn.commit()
    conn.close()

def insert_data(name, wo_number, sa_number, time_start, time_end, pdf_path):
    """Добавляет новую запись в базу"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jobs (name, wo_number, sa_number, time_start, time_end, pdf_path) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, wo_number, sa_number, time_start, time_end, pdf_path))
    conn.commit()
    conn.close()

def get_latest_entry():
    """Получает последнюю запись"""
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result