import sqlite3

conn = sqlite3.connect('history.db')
cursor = conn.cursor()
cursor.execute('''
   CREATE TABLE bookingtable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER,
    vehicle TEXT,
    fare REAL,
    source TEXT,
    destination TEXT,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

    
''')
conn.commit()
conn.close()
