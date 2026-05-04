from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import car_search, db_setup, get_car_by_id, create_payment
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime


app = Flask(__name__)

# Setup secret key for session management (for flash messages)
app.secret_key = '1234567890'  # Replace with a secure secret key

# Initializing the database
db_setup()

def setup_feedback_table():
    with sqlite3.connect('cars.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

setup_feedback_table()

def get_all_feedbacks():
    with sqlite3.connect('cars.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedbacks ORDER BY created_at DESC')
        return cursor.fetchall()

# Decorator to require login
def login_required(f):
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapped.__name__ = f.__name__  # Keep the original function name
    return wrapped


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    # Handle POST request for user registration
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    try:
        with sqlite3.connect('cars.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        flash("Username or email already exists!", "error")
        return redirect(url_for('register'))


@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')
        comment = request.form.get('comment')
        
        if not all([name, city, comment]):
            flash('Tous les champs sont requis!', 'error')
            return redirect(url_for('index'))
        
        try:
            with sqlite3.connect('cars.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO feedbacks (name, city, comment) VALUES (?, ?, ?)',
                    (name, city, comment)
                )
                conn.commit()
                flash('Merci pour votre feedback!', 'success')
        except sqlite3.Error as e:
            flash('Une erreur est survenue. Veuillez réessayer.', 'error')
            print(f"Database error: {e}")
        
        return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('cars.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):  # Assuming password is the 4th column
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    feedbacks = get_all_feedbacks()
    return render_template('index.html', feedbacks=feedbacks)


@app.route('/search', methods=['POST'])
@login_required
def search():
    data = request.form
    results = car_search(
        year=data.get('year'),
        make=data.get('make'),
        model=data.get('model'),
        style=data.get('style'),
        condition=data.get('condition'),
        max_price=data.get('max_price')
    )
    
    # Convert results into a dictionary list
    cars = [
        {
            "id": row[0],         # id
            "year": row[1],       # year
            "make": row[2],       # make
            "model": row[3],      # model
            "style": row[4],      # style
            "condition": row[5],  # condition
            "price": row[6],      # price
            "millage": row[7],    # mileage
            "image": row[8]       # image (assuming the image is the last column)
        }
        for row in results
    ]
    
    return render_template("search_results.html", cars=cars)


@app.route('/payment/<car_id>', methods=['GET'])
@login_required
def payment(car_id):
    # Fetch car details from the database using the car_id
    car = get_car_by_id(car_id)
    
    if car is None:
        flash("Car not found!", "error")
        return redirect(url_for('index'))
    
    return render_template('payment.html', car=car)


@app.route('/process_payment/<car_id>', methods=['POST'])
@login_required
def process_payment(car_id):
    # Fetch car details from the database using the car_id
    car = get_car_by_id(car_id)
    
    if car is None:
        flash("Car not found!", "error")
        return redirect(url_for('index'))
    
    # Get the data submitted in the payment form
    card_number = request.form.get('card_number')
    expiry = request.form.get('expiry')
    cvv = request.form.get('cvv')
    name = request.form.get('name')
    
    # Create a payment record (mock process for now)
    payment_id = create_payment(car_id, car['price'])
    
    if payment_id:
        flash("Payment successful!", "success")
        return render_template('payment_success.html', car=car)
    else:
        flash("Payment failed. Please try again.", "error")
        return render_template('payment_error.html')

if __name__ == "__main__":
    app.run(debug=True)
