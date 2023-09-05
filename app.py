from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import csv


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure MongoDB
app.config['MONGO_URI'] = 'mongodb://localhost/movie_ticket_booking'
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email=request.form['email']
        
        username = request.form['username']
        password = request.form['password']

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password, method='sha256')

        user = {
            'email': email,
            'username': username,
            'password': hashed_password
        }

        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user is None:
            mongo.db.users.insert_one(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose a different username.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        session['email']=email
        
        username = request.form['username']
        session['username']=username
        password = request.form['password']

        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            flash('Login successful!', 'success')
            # Add your logic to redirect to the movie ticket booking page
            return redirect(url_for('movies'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html')



# Load movie data from the CSV file and sort by release year in descending order
def load_movie_data():
    movie_data = []
    with open('data.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            movie_data.append(row)
    
    # Sort movies by release year in descending order, handling invalid date formats
    movie_data.sort(key=lambda x: (x['release date'].split('/')[-1] if '/' in x['release date'] else '', x['release date']), reverse=True)
    
    return movie_data

@app.route('/movies')
def movies():
    movie_data = load_movie_data()
    
    return render_template('movies.html', movie_data=movie_data)



available_seats = [['A1', 'A2', 'A3', 'A4', 'A5'],
                   ['B1', 'B2', 'B3', 'B4', 'B5'],
                   ['C1', 'C2', 'C3', 'C4', 'C5'],
                   ['D1', 'D2', 'D3', 'D4', 'D5']]
#available_seats = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']

@app.route('/booktickets')
def booktickets():
    return render_template('bookticket.html', seats=available_seats)

@app.route('/select_seat', methods=['POST'])
def select_seat():
    selected_seats = request.form.getlist('seat')
    if len(selected_seats) > 10:
        return "You can select a maximum of 10 seats."
    
    session['selected_seats'] = selected_seats
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    selected_seats = session.get('selected_seats', [])
    return render_template('cart.html', selected_seats=selected_seats)

@app.route('/confirm')
def confirm():
    selected_seats = session.get('selected_seats', [])
    session.pop('selected_seats', None)
    return render_template('confirm.html', selected_seats=selected_seats,msg2=session['email'],msg=session['username'])





if __name__ == '__main__':
    app.run(debug=True)
