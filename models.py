import mysql.connector
from config import MYSQL_HR_CONFIG, MYSQL_LOGISTICS_CONFIG, MYSQL_HR_SLAVE_CONFIG, MYSQL_LOGISTICS_SLAVE_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash
from contextlib import contextmanager

@contextmanager
def get_db_connection(config):
    conn = mysql.connector.connect(**config, buffered=True)
    try:
        yield conn
    finally:
        conn.close()

def get_user_info(username):
    with get_db_connection(MYSQL_HR_SLAVE_CONFIG) as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, username, email FROM users WHERE username = %s", (username,))
        return cur.fetchone()

def find_user_by_name(username):
    with get_db_connection(MYSQL_HR_SLAVE_CONFIG) as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            return cur.fetchone()
        except Exception as e:
            print(f"Ошибка поиска пользователя: {e}")
            return None

def create_user(username, email, password):
    hashed_pw = generate_password_hash(password)
    with get_db_connection(MYSQL_HR_CONFIG) as conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_pw))
            conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка регистрации: {e}")
            return False

def get_drivers_paginated(page=1, per_page=5, search=""):
    with get_db_connection(MYSQL_LOGISTICS_SLAVE_CONFIG) as conn:
        cursor = conn.cursor(dictionary=True)
        offset = (page - 1) * per_page
        
        search_pattern = f"%{search}%"
        if search:
            query = "SELECT * FROM drivers_csv WHERE ФИО LIKE %s ORDER BY ID_Водителя DESC LIMIT %s OFFSET %s"
            cursor.execute(query, (search_pattern, per_page, offset))
        else:
            query = "SELECT * FROM drivers_csv ORDER BY ID_Водителя DESC LIMIT %s OFFSET %s"
            cursor.execute(query, (per_page, offset))
        
        drivers = cursor.fetchall()
        
        count_query = "SELECT COUNT(*) as count FROM drivers_csv"
        if search:
            count_query += " WHERE ФИО LIKE %s"
            cursor.execute(count_query, (search_pattern,))
        else:
            cursor.execute(count_query)
            
        total_drivers = cursor.fetchone()['count']
        total_pages = (total_drivers + per_page - 1) // per_page
        
    return drivers, total_pages

def add_driver(full_name, license_number, phone, category, exp):
    try:
        with get_db_connection(MYSQL_LOGISTICS_CONFIG) as conn:
            cur = conn.cursor()
            cur.execute("""INSERT INTO drivers_csv (ФИО, Права, Телефон, Стаж, Статус, Регион_работы) 
                           VALUES (%s, %s, %s, %s, 'Активен', 'Москва')""",
                    (full_name, license_number, phone, exp))
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка добавления водителя: {e}")
        return False

def delete_driver(driver_id):
    with get_db_connection(MYSQL_LOGISTICS_CONFIG) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM drivers_csv WHERE ID_Водителя=%s", (driver_id,))
        conn.commit()

# --- РЕЙСЫ ---

def get_all_trips():
    with get_db_connection(MYSQL_LOGISTICS_SLAVE_CONFIG) as conn:
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute('''SELECT w.ID_накладной, w.VIN_код, d.ФИО as driver_name, 
                                  s.Наименование as store_name, p.Название as product_name,
                                  'В пути' as Статус
                           FROM waybills w
                           LEFT JOIN drivers_csv d ON w.ID_водителя = d.ID_Водителя
                           LEFT JOIN stores s ON w.Код_точки = s.Код_точки
                           LEFT JOIN products p ON w.Код_товара = p.Код_товара
                           ORDER BY w.ID_накладной DESC''')
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка получения рейсов: {e}")
            return []

def add_trip(trip_number, driver_id, route, cargo, date, status):
    try:
        with get_db_connection(MYSQL_LOGISTICS_CONFIG) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO waybills (VIN_код, ID_водителя) VALUES (%s, %s)",
                        (trip_number, driver_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"Ошибка добавления рейса: {e}")
        return False

def delete_trip(trip_id):
    with get_db_connection(MYSQL_LOGISTICS_CONFIG) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM waybills WHERE ID_накладной=%s", (trip_id,))
        conn.commit()

def get_dashboard_stats():
    with get_db_connection(MYSQL_LOGISTICS_SLAVE_CONFIG) as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) as total FROM drivers_csv")
        drivers_count = cur.fetchone()['total']
        cur.execute("SELECT COUNT(*) as total FROM waybills")
        trips_count = cur.fetchone()['total']
        
        return {
            "drivers": drivers_count,
            "trips": trips_count,
            "labels": ["Водители", "Рейсы"],
            "data": [drivers_count, trips_count]
        }
