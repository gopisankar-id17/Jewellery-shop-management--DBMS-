import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Create the book table
cursor.execute('''
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT,
    price REAL,
    stock INTEGER
);
''')

# Commit changes and close the connection
conn.commit()
print("Table 'book' created successfully in 'test.db'.")
conn.close()
