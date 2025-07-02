from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'getset_secret_key'

DB_NAME = 'getset_users.db'

# 🔧 Create the SQLite database table if it doesn't exist
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                age INTEGER,
                phone TEXT,
                address TEXT,
                medical_history TEXT
            )
        ''')
        conn.commit()

# 🏠 Redirect base route to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# ✅ Route for index.html (emergency menu)
@app.route('/index')
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        flash("Please log in to access the system.", "error")
        return redirect(url_for('login'))

# 📝 SIGN UP route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        phone = request.form['phone']
        address = request.form['address']
        medical = request.form['medical']

        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (fullname, username, password, age, phone, address, medical_history)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (fullname, username, password, age, phone, address, medical))
                conn.commit()
            flash("Signup successful. You may now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Choose a different one.", "error")

    return render_template('signup.html')

# 🔐 LOGIN route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()

        if user:
            session['user'] = user[2]  # username
            flash("Login successful.", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")

    return render_template('login.html')

# 🔓 LOGOUT route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# 🔁 Start the server
if __name__ == '__main__':
    init_db()
    app.run(debug=True)