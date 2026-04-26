from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'moy-sekretnyy-klyuch'

DB_USERS = os.path.join(os.path.dirname(__file__), 'users.db')
DB_DRIVERS = os.path.join(os.path.dirname(__file__), 'drivers.db')
DB_TRIPS = os.path.join(os.path.dirname(__file__), 'trips.db')


def init_db():
    # Инициализация базы пользователей
    conn = sqlite3.connect(DB_USERS)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    # Инициализация базы водителей
    conn = sqlite3.connect(DB_DRIVERS)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            license_number TEXT NOT NULL UNIQUE,
            phone_number TEXT NOT NULL,
            category TEXT,
            experience INTEGER
        )
    ''')
    conn.commit()
    conn.close()

    # Инициализация базы рейсов
    conn = sqlite3.connect(DB_TRIPS)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_number TEXT NOT NULL UNIQUE,
            driver_name TEXT NOT NULL,
            route TEXT NOT NULL,
            cargo TEXT,
            departure_date TEXT,
            arrival_date TEXT,
            distance INTEGER,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_user(username, email, password):
    try:
        conn = sqlite3.connect(DB_USERS)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def save_driver(full_name, license_number, phone_number, category, experience):
    try:
        conn = sqlite3.connect(DB_DRIVERS)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO drivers (full_name, license_number, phone_number, category, experience) 
               VALUES (?, ?, ?, ?, ?)''',
            (full_name, license_number, phone_number, category, experience)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def save_trip(trip_number, driver_name, route, cargo, departure_date, arrival_date, distance, status):
    try:
        conn = sqlite3.connect(DB_TRIPS)
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO trips (trip_number, driver_name, route, cargo, departure_date, arrival_date, distance, status) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (trip_number, driver_name, route, cargo, departure_date, arrival_date, distance, status)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def check_user(username, password):
    conn = sqlite3.connect(DB_USERS)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user is not None



init_db()


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Пароли не совпадают!', 'error')
            return redirect(url_for('register'))

        if not username or not email or not password:
            flash('Все поля обязательны!', 'error')
            return redirect(url_for('register'))

        success = save_user(username, email, password)

        if success:
            flash('Регистрация прошла успешно! Теперь войдите.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Это имя уже занято!', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if check_user(username, password):
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неправильное имя или пароль!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/add_driver', methods=['POST'])
def add_driver():
    full_name = request.form.get('full_name')
    license_number = request.form.get('license_number')
    phone_number = request.form.get('phone_number')
    category = request.form.get('category')
    experience = request.form.get('experience')

    if not full_name or not license_number:
        flash('ФИО и номер прав обязательны!', 'error')
        return redirect(url_for('index'))

    success = save_driver(full_name, license_number, phone_number, category, experience)
    if success:
        flash('Водитель успешно добавлен!', 'success')
    else:
        flash('Ошибка при добавлении водителя (возможно, номер прав уже есть).', 'error')
    
    return redirect(url_for('index'))


@app.route('/add_trip', methods=['POST'])
def add_trip():
    trip_number = request.form.get('trip_number')
    driver_name = request.form.get('driver_name')
    route = request.form.get('route')
    cargo = request.form.get('cargo')
    departure_date = request.form.get('departure_date')
    arrival_date = request.form.get('arrival_date')
    distance = request.form.get('distance')
    status = request.form.get('status')

    if not trip_number or not driver_name or not route:
        flash('Номер рейса, водитель и маршрут обязательны!', 'error')
        return redirect(url_for('index'))

    success = save_trip(trip_number, driver_name, route, cargo, departure_date, arrival_date, distance, status)
    if success:
        flash('Рейс успешно добавлен!', 'success')
    else:
        flash('Ошибка при добавлении рейса.', 'error')
    
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return 'Страница не найдена', 404



if __name__ == '__main__':
    app.run(debug=True)
