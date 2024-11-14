from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
import os 
import requests

app = Flask(__name__)
app.secret_key = 'sxadxasdaspodk7898754asdas'


app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/car_images')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'car_sales_db'

# Initialize MySQL
mysql = MySQL(app)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Store plain text password directly
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        print(user) 
        print(user,user[2])
        # Compare plain text password
        if user and user[2] == password:  # Assuming password is at index 2
            session['username'] = username
            session['is_admin'] = user[3]  # Assuming 'is_admin' is at index 3
            flash('Login successful!', 'success')
            return redirect(url_for('list_cars'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/list_cars')
def list_cars():
    try:
        # Create a cursor to execute SQL queries
        cur = mysql.connection.cursor()
        
        # Execute the query to fetch all cars
        cur.execute('SELECT * FROM cars')
        cars = cur.fetchall()  # Fetch all rows from the executed query
        print(cars)  # Debugging: print the result to the console
        
        # Check if the logged-in user has rented any cars
        rented_cars = set()
        if 'username' in session:
            cur.execute('SELECT car_id FROM rent_contracts WHERE user_id = (SELECT id FROM users WHERE username = %s)', (session['username'],))
            rented_cars = {car[0] for car in cur.fetchall()}  # Set of rented car IDs
        
        cur.close()  # Close the cursor after use

        # Fetch car-related news articles from the API
        NEWS_API_URL = "https://newsapi.org/v2/everything"
        NEWS_API_KEY = "45f48158502d45b9a3b23f2d9924561e"  # Your News API key

        params = {
            'q': 'car_news',  # Query term
            'apiKey': NEWS_API_KEY,
            'language': 'en',
            'pageSize': 5,  # Number of news articles to fetch
        }
        response = requests.get(NEWS_API_URL, params=params)
        news_data = response.json()

        # Check if the request was successful
        if news_data.get('status') == 'ok':
            articles = news_data['articles']
        else:
            articles = []

        # Pass the fetched cars, rented cars, and news articles to the template
        return render_template('cars.html', cars=cars, rented_cars=rented_cars, articles=articles)

    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred while fetching data', 'danger')
        return render_template('cars.html', cars=[], rented_cars=set(), articles=[])


# Admin-only routes
def admin_required():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('list_cars'))
    

supported_extensions = {'png', 'jpg', 'jpeg', 'gif'}



def image_extensions(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in supported_extensions

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('list_cars'))

    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']
        mileage = request.form['mileage']
        
        # Handle image upload
        image = request.files.get('image')
        image_filename = None
        if image and image_extensions(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Insert car into the database
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO cars (make, model, year, price, mileage, image) VALUES (%s, %s, %s, %s, %s, %s)',
            (make, model, year, price, mileage, image_filename)
        )
        mysql.connection.commit()
        cur.close()
        flash('Car added successfully', 'success')
        return redirect(url_for('list_cars'))

    return render_template('add_car.html')

@app.route('/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('list_cars'))

    # Get the car details from the database
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM cars WHERE id = %s', (car_id,))
    car = cur.fetchone()

    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']
        mileage = request.form['mileage']

        # Handle image upload
        image = request.files.get('image')
        image_filename = car[6]  # Keep existing image if no new image is uploaded
        if image and image_extensions(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Update the car details in the database
        cur.execute(
            'UPDATE cars SET make = %s, model = %s, year = %s, price = %s, mileage = %s, image = %s WHERE id = %s',
            (make, model, year, price, mileage, image_filename, car_id)
        )
        mysql.connection.commit()  # Commit changes
        cur.close()
        flash('Car updated successfully', 'success')
        return redirect(url_for('list_cars'))

    cur.close()  # Always close the cursor after the operation
    return render_template('edit_car.html', car=car)


# Rent car route
@app.route('/rent_car/<int:car_id>', methods=['POST'])
def rent_car(car_id):
    if 'username' not in session:
        flash('Please log in to rent a car', 'danger')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute('SELECT id FROM users WHERE username = %s', (session['username'],))
    user = cur.fetchone()

    print(user)
    cur.execute(
        'INSERT INTO rent_contracts (user_id, car_id) VALUES (%s, %s)',
        (user[0], car_id)  # Assuming user ID is at index 0
    )
    mysql.connection.commit()
    cur.close()
    flash('Car rented successfully!', 'success')
    return redirect(url_for('list_cars'))

# Admin: Manage contracts
@app.route('/manage_contracts')
def manage_contracts():
    if not session.get('is_admin'):
        flash('Admin access required', 'danger') 
        return redirect(url_for('list_cars'))

    try:
        cur = mysql.connection.cursor()
        cur.execute('''SELECT rent_contracts.id, rent_contracts.rental_date, users.username, cars.make, cars.model
                       FROM rent_contracts
                       JOIN users ON rent_contracts.user_id = users.id
                       JOIN cars ON rent_contracts.car_id = cars.id''')
        contracts = cur.fetchall()  # Fetch all rows
        print(contracts)
        cur.close()
        
        return render_template('manage_contracts.html', contracts=contracts)
    
    except Exception as e:
        # Handle any database errors
        print(f"Error fetching contracts: {e}")
        flash('Error fetching contracts. Please try again later.', 'danger')
        return redirect(url_for('list_cars'))



@app.route('/delete_car/<int:car_id>')
def delete_car(car_id):
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Create a cursor to interact with the MySQL database
        cur = mysql.connection.cursor()
        
        # Execute the query to delete the car with the specified id
        cur.execute('DELETE FROM cars WHERE id = %s', (car_id,))
        mysql.connection.commit()  # Commit the change to the database
        cur.close()  # Close the cursor after use

        # Show a success message and redirect to the car list
        flash('Car deleted successfully', 'success')
    except Exception as e:
        # Handle errors and show an error message
        flash(f"Error occurred: {str(e)}", 'danger')
    
    return redirect(url_for('list_cars'))



@app.route('/delete_contract/<int:contract_id>')
def delete_contract(contract_id):
    if not session.get('is_admin'):
        flash('Admin access required', 'danger')
        return redirect(url_for('manage_contracts'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM rent_contracts WHERE id = %s', (contract_id,))
    mysql.connection.commit()
    cur.close()
    flash('Contract deleted successfully', 'success')
    return redirect(url_for('manage_contracts'))

# Main page route
@app.route('/')
def index():
    return redirect(url_for('list_cars'))

if __name__ == '__main__':
    app.run(debug=True)
