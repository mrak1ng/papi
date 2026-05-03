from flask import Flask, render_template, request, redirect, url_for, flash
import database
import os

app = Flask(__name__)
app.secret_key = 'moy-sekretnyy-klyuch'

database.init_db()

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

        success = database.create_user(username, email, password)

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

        if database.check_user(username, password):
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неправильное имя или пароль!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/index')
def index():
    drivers = database.get_all_drivers()
    trips = database.get_all_trips()
    
    # Передаем списки в шаблон для отображения таблиц
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

    success = database.create_driver(full_name, license_number, phone_number, category, experience)
    if success:
        flash('Водитель успешно добавлен!', 'success')
    else:
        flash('Ошибка при добавлении (номер прав уже есть).', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_driver/<int:id>')
def delete_driver(id):
    database.delete_driver(id)
    flash('Водитель удален.', 'success')
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

    success = database.create_trip(trip_number, driver_name, route, cargo, departure_date, arrival_date, distance, status)
    if success:
        flash('Рейс успешно добавлен!', 'success')
    else:
        flash('Ошибка при добавлении рейса.', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete_trip/<int:id>')
def delete_trip(id):
    database.delete_trip(id)
    flash('Рейс удален.', 'success')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return 'Страница не найдена', 404


if __name__ == '__main__':
    app.run(debug=True)
