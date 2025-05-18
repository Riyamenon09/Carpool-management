import sqlite3

def create_database():
    connection = sqlite3.connect('drivers.db')  # Creating a new SQLite database named drivers.db
    cursor = connection.cursor()

    # Create a table for drivers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_name TEXT NOT NULL,
            gender TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            address TEXT NOT NULL,
            dob TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            license_plate TEXT NOT NULL,
            insurance_number TEXT NOT NULL,
            registration_date TEXT NOT NULL
        )
    ''')

    connection.commit()
    connection.close()

if __name__ == '__main__':
    create_database()
