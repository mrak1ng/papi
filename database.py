import mysql.connector
from config import MYSQL_HR_CONFIG, MYSQL_LOGISTICS_CONFIG

def check_connections():
    try:
        conn_hr = mysql.connector.connect(**MYSQL_HR_CONFIG)
        conn_hr.close()
        print("✅ Подключение к mysql_hr успешно")
        conn_log = mysql.connector.connect(**MYSQL_LOGISTICS_CONFIG)
        conn_log.close()
        print("✅ Подключение к mysql_logistics успешно")
        
    except Exception as e:
        print(f"❌ Ошибка подключения к MySQL: {e}")
        raise e