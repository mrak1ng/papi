from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from config import SECRET_KEY
from models import get_drivers_paginated, add_driver, delete_driver, get_all_trips, delete_trip
from auth import handle_login, handle_register
import jwt
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = SECRET_KEY

SUPPORT_API_URL = "http://127.0.0.1:8000"

# Декоратор для защиты роутов (требование PDF)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            flash("Пожалуйста, войдите в систему", "error")
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # Можно добавить проверку пользователя в БД здесь
        except:
            flash("Сессия истекла или недействительна", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        success, result = handle_login(username, password)
        if success:
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('token', result) # Сохраняем JWT в куки
            return resp
        else:
            flash(result, 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        success, msg = handle_register(username, email, password, confirm)
        if success:
            flash(msg, 'success')
            return redirect(url_for('login'))
        else:
            flash(msg, 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('token')
    return resp

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/refresh_token', methods=['POST'])
@token_required
def refresh_token():
    """Обновление токена через API (возвращает новый токен в JSON)"""
    from auth import generate_jwt
    token = request.cookies.get('token')
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = data.get('username')
    
    new_token = generate_jwt(username)
    
    # Можно вернуть и в куках, и в теле ответа для гибкости
    resp = make_response({"message": "Токен обновлен", "new_token": new_token})
    resp.set_cookie('token', new_token)
    return resp

@app.route('/index')
@token_required
def index():
    token = request.cookies.get('token')
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    username = data.get('username')

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    drivers, total_pages = get_drivers_paginated(page=page, search=search)
    trips = get_all_trips()

    return render_template('index.html', 
                           drivers=drivers, 
                           trips=trips,
                           current_page=page,       
                           total_pages=total_pages, 
                           search_query=search,
                           username=username)

@app.route('/dashboard')
@token_required
def dashboard():
    """Эндпоинт для аналитики (требование PDF).
    Тут будут графики (в шаблоне используем Chart.js)"""
    return render_template('dashboard.html')

@app.route('/api/stats')
@token_required
def api_stats():
    """API эндпоинт для динамической статистики (Чистый Backend)"""
    from models import get_dashboard_stats
    stats = get_dashboard_stats()
    return stats

@app.route('/api/hash/<text>')
def hash_proxy(text):
    """Прокси-роут к FastAPI с обработкой падения сервиса (Fallback)"""
    try:
        response = requests.get(f"{SUPPORT_API_URL}/api/hash/{text}", timeout=2)
        return response.json()
    except Exception as e:
        print(f"DEBUG: Ошибка при вызове FastAPI (hash): {e}")
        # Резервный ответ (требование PDF)
        import hashlib
        local_hash = hashlib.sha256(text.encode()).hexdigest()
        return {
            "request": text,
            "result": local_hash,
            "note": "Внимание: сервис FastAPI недоступен, использован локальный метод."
        }

@app.route('/about')
def about_html():
    """HTML страница + данные из микросервиса с Fallback"""
    about_data = {}
    try:
        response = requests.get(f"{SUPPORT_API_URL}/api/about", timeout=2)
        about_data = response.json()
    except Exception as e:
        print(f"DEBUG: Ошибка при вызове FastAPI (about): {e}")
        about_data = {
            "project_name": "CargoPay (Offline Mode)",
            "description": "Описание временно недоступно, так как сервис поддержки выключен."
        }
    return render_template('about.html', about=about_data)

@app.route('/api/about')
def about_json_proxy():
    """JSON роут о проекте с Fallback (требование PDF)"""
    try:
        return requests.get(f"{SUPPORT_API_URL}/api/about", timeout=2).json()
    except Exception as e:
        print(f"DEBUG: Ошибка при вызове FastAPI (api/about): {e}")
        return {"error": "Сервис недоступен", "fallback": "Используйте локальный about.json"}

@app.route('/add_driver', methods=['POST'], endpoint='add_driver')
@token_required
def add_driver_route():
    full_name = request.form.get('full_name')
    license_number = request.form.get('license_number')
    phone_number = request.form.get('phone_number')
    category = request.form.get('category')
    experience = request.form.get('experience')

    if not full_name or not license_number:
        flash('ФИО и номер прав обязательны!', 'error')
        return redirect(url_for('index'))

    success = add_driver(full_name, license_number, phone_number, category, experience)
    if success:
        flash('Водитель успешно добавлен!', 'success')
    else:
        flash('Ошибка при добавлении водителя.', 'error')

    return redirect(url_for('index'))

@app.route('/add_trip', methods=['POST'], endpoint='add_trip')
@token_required
def add_trip_route():
    from models import add_trip
    trip_number = request.form.get('trip_number')
    driver_name = request.form.get('driver_name') 
    status = request.form.get('status')

    if not trip_number or not driver_name:
        flash('Заполните обязательные поля (Номер и Водитель)!', 'error')
        return redirect(url_for('index'))


    success = add_trip(trip_number, 1, "Route", "Cargo", "Date", status)
    if success:
        flash('Рейс успешно создан!', 'success')
    else:
        flash('Ошибка БД при создании рейса (проверьте колонки)', 'error')

    return redirect(url_for('index'))

@app.route('/delete_driver/<int:id>')
@token_required
def del_driver(id):
    delete_driver(id)
    return redirect(url_for('index'))

@app.route('/delete_trip/<int:id>')
@token_required
def del_trip(id):
    delete_trip(id)
    return redirect(url_for('index'))

@app.route('/update_account', methods=['POST'])
@token_required
def update_account():
    """Обновление настроек аккаунта (заглушка)"""
    flash('Настройки аккаунта обновлены!', 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
if __name__ == '__main__':
    app.run(debug=True)