import sqlite3

DATABASE_NAME = "assistant_bot.db"

def connect_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn, conn.cursor()

def create_tables():
    conn, cursor = connect_db()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        preferred_location TEXT,
        preferred_currencies TEXT,
        notifications_enabled INTEGER DEFAULT 0,
        morning_reminder_enabled INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        timestamp TIMESTAMP,
        temperature REAL,
        humidity REAL,
        wind_speed REAL,
        description TEXT,
        raw_data TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS currency_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base_currency TEXT,
        target_currency TEXT,
        rate REAL,
        timestamp TIMESTAMP,
        raw_data TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS air_raid_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT,
        status TEXT,
        timestamp TIMESTAMP,
        raw_data TEXT
    )
    """)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN morning_reminder_enabled INTEGER DEFAULT 0")
        conn.commit()
        print("Столбец morning_reminder_enabled успешно добавлен в таблицу users.")
    except sqlite3.OperationalError:
        print("Столбец morning_reminder_enabled уже существует в таблице users.")
    conn.commit()
    conn.close()