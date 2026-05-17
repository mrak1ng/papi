# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'moy-sekretnyy-klyuch'

DB_USERS = os.path.join(os.path.dirname(__file__), 'users.db')
DB_DRIVERS = os.path.join(os.path.dirname(__file__), 'drivers.db')
DB_TRIPS = os.path.join(os.path.dirname(__file__), 'trips.db')

def init_db():
    conn = sqlite3.connect(DB_USERS)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL, password TEXT NOT NULL)''')
    conn.commit(); conn.close()

    conn = sqlite3.connect(DB_DRIVERS)
    conn.execute('''CREATE TABLE IF NOT EXISTS drivers (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, license_number TEXT NOT NULL UNIQUE, phone_number TEXT NOT NULL, category TEXT, experience INTEGER)''')
    conn.commit(); conn.close()

    conn = sqlite3.connect(DB_TRIPS)
    conn.execute('''CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY AUTOINCREMENT, trip_number TEXT NOT NULL UNIQUE, driver_name TEXT NOT NULL, route TEXT NOT NULL, cargo TEXT, departure_date TEXT, arrival_date TEXT, distance INTEGER, status TEXT)''')
    conn.commit(); conn.close()

def get_all_drivers():
    conn = sqlite3.connect(DB_DRIVERS)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM drivers ORDER BY id DESC') # Сортируем по новизне
    drivers = cursor.fetchall()
    conn.close()
    return drivers

def get_all_trips():
    conn = sqlite3.connect(DB_TRIPS)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trips ORDER BY id DESC')
    trips = cursor.fetchall()
    conn.close()
    return trips

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

# Конфигурация
MYSQL_LOGISTICS = {
    'host': 'localhost', 'user': 'root', 'password': '123123',
    'database': 'mysql_logistics', 'charset': 'utf8mb4', 'autocommit': True
}
MYSQL_HR = {
    'host': 'localhost', 'user': 'root', 'password': '123123',
    'database': 'mysql_hr', 'charset': 'utf8mb4', 'autocommit': True
}

def init_mysql_dbs():
    """Создаёт 2 базы и таблицы, максимально повторяя заголовки твоих CSV."""
    try:
        #Создаём БД
        root = mysql.connector.connect(host='localhost', user='root', password='123123')
        cur_root = root.cursor()
        cur_root.execute("CREATE DATABASE IF NOT EXISTS mysql_logistics")
        cur_root.execute("CREATE DATABASE IF NOT EXISTS mysql_hr")
        root.close()

        #Таблицы для БД 1
        conn1 = mysql.connector.connect(**MYSQL_LOGISTICS)
        cur1 = conn1.cursor()
        cur1.execute('''CREATE TABLE IF NOT EXISTS stores (
            Код_точки INT PRIMARY KEY, Наименование VARCHAR(100), Адрес VARCHAR(200),
            Телефон_ответственного VARCHAR(20), Режим_работы VARCHAR(50),
            Контактное_лицо VARCHAR(100), Приоритет_доставки VARCHAR(20)
        )''')
        cur1.execute('''CREATE TABLE IF NOT EXISTS drivers_csv (
            ID_Водителя INT PRIMARY KEY, ФИО VARCHAR(100), Права VARCHAR(20),
            Телефон VARCHAR(20), Стаж INT, Статус VARCHAR(30), Регион_работы VARCHAR(50)
        )''')
        cur1.execute('''CREATE TABLE IF NOT EXISTS products (
            Код_товара INT PRIMARY KEY, Название VARCHAR(100), Категория VARCHAR(50),
            Единица_измерения VARCHAR(10), Вес_единицы INT, Габариты VARCHAR(50), Цена_за_единицы DECIMAL(10,2)
        )''')
        cur1.execute('''CREATE TABLE IF NOT EXISTS waybills (
            ID_накладной INT PRIMARY KEY, Код_товара INT, ID_водителя INT,
            Код_точки INT, VIN_код VARCHAR(30)
        )''')
        cur1.execute('''CREATE TABLE IF NOT EXISTS vehicles (
            VIN_код VARCHAR(30) PRIMARY KEY, Гос_номер VARCHAR(20), Модель VARCHAR(50),
            Грузоподъёмность DECIMAL(10,2), Объём_кузова DECIMAL(10,2), Дата_ТО DATETIME, Пробег INT
        )''')
        conn1.close()

        #Таблицы для БД 2
        conn2 = mysql.connector.connect(**MYSQL_HR)
        cur2 = conn2.cursor()
        cur2.execute('''CREATE TABLE IF NOT EXISTS worked_time (
            ID_Записи INT PRIMARY KEY, ID_Сотрудника INT,
            Дата_начала DATETIME, Дата_окончания DATETIME, Кол_часов INT, Месяц INT, Год INT
        )''')
        cur2.execute('''CREATE TABLE IF NOT EXISTS salary_accruals (
            ID_Начисления INT PRIMARY KEY, ID_Сотрудника INT, Сумма_базовая DECIMAL(10,2),
            Налоги DECIMAL(10,2), ID_Записи INT
        )''')
        cur2.execute('''CREATE TABLE IF NOT EXISTS bonuses (
            ID_Премии INT PRIMARY KEY, Процент_премии DECIMAL(5,2), Основание VARCHAR(200)
        )''')
        cur2.execute('''CREATE TABLE IF NOT EXISTS employees (
            ID_Сотрудника INT PRIMARY KEY, ФИО VARCHAR(100), Телефон VARCHAR(20),
            Email VARCHAR(100), Должность VARCHAR(50), Почасовой_оклад DECIMAL(10,2), Подразделение VARCHAR(50)
        )''')
        cur2.execute('''CREATE TABLE IF NOT EXISTS payroll_orders (
            ID_Распоряжения INT PRIMARY KEY, ID_Премии INT, ID_Начисления INT,
            Год INT, Месяц INT, ID_Сотрудника INT
        )''')
        conn2.close()
        print("✅ MySQL базы и таблицы успешно созданы.")
    except mysql.connector.Error as e:
        print(f"⚠️ MySQL пока не запущен или ошибка пароля: {e}")
        print("💡 Сайт продолжит работать на SQLite. MySQL подключится позже.")


def add_to_mysql(db_config, table_name, data_tuple):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        placeholders = ', '.join(['%s'] * len(data_tuple))  # генерирует %s, %s, %s...
        cursor.execute(f'INSERT INTO {table_name} VALUES ({placeholders})', data_tuple)
        print(f"✅ Запись добавлена в {table_name}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при записи в {table_name}: {e}")
        return False
    finally:
        conn.close()

# Запуск инициализации при старте
init_db()
init_mysql_dbs()

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
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
    drivers = get_all_drivers()
    trips = get_all_trips()
    return render_template('index.html', drivers=drivers, trips=trips)

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

@app.route('/update_account', methods=['POST'])
def update_account():
    # Получаем данные из формы
    new_login = request.form.get('new_login')
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')


    flash('Настройки аккаунта сохранены! (Логика обновления в разработке)', 'success')
    return redirect(url_for('index'))

@app.route('/delete_driver/<int:driver_id>')
def delete_driver(driver_id):
    conn = sqlite3.connect(DB_DRIVERS)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM drivers WHERE id = ?', (driver_id,))
    conn.commit()
    conn.close()
    flash('Водитель удален.', 'success')
    return redirect(url_for('index', tab='drivers'))

@app.route('/delete_trip/<int:trip_id>')
def delete_trip(trip_id):
    conn = sqlite3.connect(DB_TRIPS)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
    conn.commit()
    conn.close()
    flash('Рейс удален.', 'success')
    return redirect(url_for('index', tab='trips'))

init_db()

if __name__ == '__main__':
    app.run(debug=True)