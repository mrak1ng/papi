import os
from dotenv import load_dotenv

load_dotenv()

import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_HR_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': 'mysql_hr',
    'charset': 'utf8mb4'
}

MYSQL_HR_SLAVE_CONFIG = MYSQL_HR_CONFIG.copy()

MYSQL_LOGISTICS_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': 'mysql_logistics',
    'charset': 'utf8mb4'
}

MYSQL_LOGISTICS_SLAVE_CONFIG = MYSQL_LOGISTICS_CONFIG.copy()
SUPPORT_API_URL = os.getenv('SUPPORT_API_URL', 'http://127.0.0.1:8000')