import sqlite3

# Connect to the SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('history.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the bookings table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ride_id TEXT NOT NULL,
    driver_name TEXT NOT NULL,
    fare REAL NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Bookings table created successfully!")
