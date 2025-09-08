# db_init.py
import sqlite3

conn = sqlite3.connect("data.db")
c = conn.cursor()

# Table crypto
c.execute("""
CREATE TABLE IF NOT EXISTS crypto (
    time TEXT,
    name TEXT,
    price REAL
)
""")

# Table hardware
c.execute("""
CREATE TABLE IF NOT EXISTS hardware (
    time TEXT,
    product TEXT,
    price REAL
)
""")

# Table esport
c.execute("""
CREATE TABLE IF NOT EXISTS esport (
    time TEXT,
    game TEXT,
    metric TEXT,
    value REAL
)
""")

conn.commit()
conn.close()
print("✅ Base SQLite initialisée")


