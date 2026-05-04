import sqlite3

def db_setup():
    """Create and populate the database with an additional column for images and payment table."""
    connection = sqlite3.connect('cars.db')  # This creates the `cars.db` file if it doesn't exist.
    cursor = connection.cursor()
    
    # Create the 'users' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
    # Create the cars table with an additional `image` column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            make TEXT,
            model TEXT,
            style TEXT,
            condition TEXT,
            price REAL,
            millage INTEGER,
            image TEXT
        )
    ''')

    # Create the payments table to record payment information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER,
            amount REAL,
            status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (car_id) REFERENCES cars (id)
        )
    ''')

    # Check if the table is empty before inserting data
    cursor.execute('SELECT COUNT(*) FROM cars')
    count = cursor.fetchone()[0]

    if count == 0:  # Only insert data if the table is empty
        # Populate the table with static data, including images
        cursor.executemany('''
            INSERT INTO cars (year, make, model, style, condition, price, millage, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            (2020, 'Audi', 'RS6', 'Sedan', 'Used', 80000, 15000, 'audi_rs6.jpg'),
            (2021, 'Cupra', 'Formentor', 'SUV', 'Used', 35000, 10000, 'cupra_formentor.jpg'),
            (2019, 'Dacia', 'Duster', 'SUV', 'Used', 15000, 20000, 'dacia_duster.jpg'),
            (2022, 'Skoda', 'Octavia', 'Hatchback', 'Used', 22000, 5000, 'skoda_octavia.jpg'),
            (2023, 'Peugeot', '208', 'Hatchback', 'Used', 25000, 3000, 'R (1).jpeg'),
            (2020, 'Audi', 'Q5', 'SUV', 'Used', 50000, 9000, 'fc4.png'),
            (2018, 'Cupra', 'Leon', 'Hatchback', 'Used', 22000, 25000, 'new-cupra-leon-five-doors-e-hybrid-compact-sports-car-in-magnetic-tech-matte-specifications.jpg'),
            (2022, 'Dacia', 'Sandero', 'Hatchback', 'Used', 13000, 7000, 'OIP.jpeg'),
            (2019, 'Skoda', 'Superb', 'Sedan', 'Used', 30000, 18000, 'R.png'),
            (2023, 'Opel', 'Insignia', 'Sedan', 'Used', 30000, 4000, 'OIP (1).jpeg'),
            (2020, 'Peugeot', '3008', 'SUV', 'Used', 27000, 6000, 'OIP (2).jpeg'),
            (2021, 'Mercedes', 'A-Class', 'Hatchback', 'Used', 35000, 5000, 'R.jpeg'),
            (2021, 'Audi', 'A4', 'Sedan', 'Used', 45000, 7500, 'R (2).jpeg'),
        ])

    connection.commit()
    connection.close()
    print("Database setup complete.")

def car_search(year=None, make=None, model=None, style=None, condition=None, max_price=None):
    """Query the database based on user input and include image data."""
    query = "SELECT * FROM cars WHERE 1=1"
    params = []

    if year:
        query += " AND year = ?"
        params.append(int(year))
    if make:
        query += " AND make = ?"
        params.append(make)
    if model:
        query += " AND model = ?"
        params.append(model)
    if style:
        query += " AND style = ?"
        params.append(style)
    if condition:
        query += " AND condition = ?"
        params.append(condition)
    if max_price:
        query += " AND price <= ?"
        params.append(float(max_price))

    connection = sqlite3.connect('cars.db')
    cursor = connection.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()

    connection.close()

    return results

def get_car_by_id(car_id):
    """Retrieve a car from the database by its ID."""
    connection = sqlite3.connect('cars.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
    car = cursor.fetchone()
    connection.close()
    if car:
        return {
            "id": car[0],
            "year": car[1],
            "make": car[2],
            "model": car[3],
            "style": car[4],
            "condition": car[5],
            "price": car[6],
            "millage": car[7],
            "image": car[8]
        }
    return None

def create_payment(car_id, amount):
    """Record a payment for a car purchase."""
    connection = sqlite3.connect('cars.db')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO payments (car_id, amount, status)
        VALUES (?, ?, ?)
    ''', (car_id, amount, 'successful'))
    payment_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return payment_id

def get_user_by_username(username):
    """
    Retrieve user details by username.
    """
    with sqlite3.connect('cars.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()
    