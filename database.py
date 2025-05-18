import sqlite3

def create_database():
    connection = sqlite3.connect('carpool.db')
    cursor = connection.cursor()

    # Create a table for users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    connection.commit()
    connection.close()

if __name__ == '__main__':
    create_database()
