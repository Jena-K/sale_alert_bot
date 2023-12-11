import sqlite3

# Connect to or create an SQLite database file
conn = sqlite3.connect('keywords.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table to store keywords
cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        idx INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        keyword TEXT NOT NULL
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()