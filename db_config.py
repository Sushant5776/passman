import sqlite3

conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT,
              password TEXT,
              website TEXT)''')
conn.commit()