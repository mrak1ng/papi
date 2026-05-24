import jwt
import datetime
from config import SECRET_KEY
from models import find_user_by_name, create_user
from werkzeug.security import check_password_hash

def generate_jwt(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def handle_login(username, password):
    user = find_user_by_name(username)
    if user and check_password_hash(user['password'], password):
        token = generate_jwt(username)
        return True, token
    return False, "Неверный логин или пароль"

def handle_register(username, email, password, confirm_pass):
    if password != confirm_pass:
        return False, "Пароли не совпадают"
    
    if find_user_by_name(username):
        return False, "Пользователь с таким именем уже существует"

    if create_user(username, email, password):
        return True, "Регистрация успешна"
    return False, "Ошибка при создании пользователя"