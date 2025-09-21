import sqlite3
import hashlib
import os
from datetime import date, timedelta
from Parts.configserver import ADMIN_KEY

# Глобальная переменная для имени пользователя
name_user = None

def hash_password(password, salt):
    """Хеширование пароля с солью"""
    return hashlib.sha256((salt + password).encode()).hexdigest()

def generate_salt():
    """Генерация соли"""
    return os.urandom(16).hex()

def initialize_databases():
    """Инициализация баз данных"""
    # База пользователей
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER UNIQUE NOT NULL,
                    name VARCHAR(20) UNIQUE NOT NULL,
                    password VARCHAR(50) NOT NULL,
                    salt TEXT,
                    lastseen DATE,
                    status VARCHAR(20) DEFAULT "Пользователь",
                    balance INTEGER DEFAULT 5000
                )''')
            db.commit()
            
    except Exception as e:
        print(f"Ошибка при инициализации базы пользователей: {e}")
    
    # База администраторов
    try:
        with sqlite3.connect("./DATA_ADMIN.DB") as db:
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER UNIQUE NOT NULL
                )''')
            db.commit()
            
    except Exception as e:
        print(f"Ошибка при инициализации базы администраторов: {e}")

def add_admin(user_id):
    """Добавление администратора"""
    try:
        with sqlite3.connect("./DATA_ADMIN.DB") as db:
            cursor = db.cursor()
            cursor.execute("INSERT OR IGNORE INTO admins (chat_id) VALUES (?)", (user_id,))
            db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при добавлении админа: {e}")
        return False

def add_user(user_id, username, hashed_password, salt):
    """Добавление пользователя"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO users (id, name, password, salt, lastseen) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, hashed_password, salt, date.today())
            )
            db.commit()
            return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Ошибка при регистрации пользователя: {e}")
        return False

def delete_user(user_id):
    """Удаление пользователя"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
        return False

def update_user_balance(user_id, amount):
    """Обновление баланса пользователя"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?",
                (amount, user_id)
            )
            db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при обновлении баланса: {e}")
        return False

def get_user_credentials(username):
    """Получение учетных данных пользователя"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute("SELECT password, salt FROM users WHERE name = ?", (username,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении учетных данных: {e}")
        return None

def update_user_last_seen(user_id, username):
    """Обновление времени последнего входа"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE users SET lastseen = ?, id = ? WHERE name = ?",
                (date.today(), user_id, username)
            )
            db.commit()
            return True
    except Exception as e:
        print(f"Ошибка при обновлении последнего входа: {e}")
        return False

def get_user_info(user_id):
    """Получение информации о пользователе"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT name, status, balance FROM users WHERE id = ?",
                (user_id,)
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return None

def check_user_exists(user_id):
    """Проверка существования пользователя"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False

def get_all_users():
    """Получение всех пользователей"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка пользователей: {e}")
        return []

def get_all_admins():
    """Получение всех администраторов"""
    try:
        with sqlite3.connect("./DATA_ADMIN.DB") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM admins")
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка администраторов: {e}")
        return []

def check_admins_db(user_id):
    """Проверка прав администратора"""
    try:
        with sqlite3.connect("./DATA_ADMIN.DB") as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM admins WHERE chat_id = ?", (user_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке администратора: {e}")
        return False

def clear_admins_db():
    """Очистка таблицы администраторов"""
    try:
        with sqlite3.connect("./DATA_ADMIN.DB") as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM admins")
            db.commit()
            print("Список админов очищен!")
    except Exception as e:
        print(f"Ошибка при очистке таблицы admins: {e}")

def delete_inactive_accounts_db():
    """Удаление неактивных аккаунтов"""
    try:
        with sqlite3.connect("./DATA.DB") as db:
            cursor = db.cursor()
            date_threshold = date.today() - timedelta(days=190)
            cursor.execute(
                "DELETE FROM users WHERE lastseen <= ?",
                (date_threshold,)
            )
            db.commit()
            print("Неактивные аккаунты удалены")
    except Exception as e:
        print(f"Ошибка при удалении неактивных аккаунтов: {e}")

# Функции для совместимости
def set_user_name(name):
    """Установка имени пользователя"""
    global name_user
    name_user = name

def save_info_user(user_id, password):
    """Сохранение информации о пользователе"""
    global name_user
    
    if not name_user or len(password) >= 30:
        return False
    
    # Проверка на администратора
    if name_user == "ADMIN" and password == ADMIN_KEY:
        return add_admin(user_id)
    
    # Регистрация обычного пользователя
    salt = generate_salt()
    hashed_password = hash_password(password, salt)
    
    return add_user(user_id, name_user, hashed_password, salt)

def set_skm_user(user_id, amount):
    """Пополнение баланса пользователя"""
    return update_user_balance(user_id, amount)

def list_users():
    """Получение списка всех пользователей"""
    users = get_all_users()
    if not users:
        return "База пуста"
    
    info_lines = []
    for user in users:
        info_lines.append(
            f"id: {user[0]}\nИмя: {user[1]}\nПароль: {user[2]}\n"
            f"Соль: {user[3]}\nДата последнего визита: {user[4]}\n"
            f"Статус: {user[5]}\nБаланс: {user[6]}\n"
        )
    
    return "\n".join(info_lines)

def list_admins():
    """Получение списка администраторов"""
    admins = get_all_admins()
    if not admins:
        return "Администраторы не найдены"
    
    info_lines = []
    for admin in admins:
        info_lines.append(f"ID:{admin[0]}\nKey:{admin[1]}\n")
    
    return "\n".join(info_lines)

def enter_user(username, password, user_id):
    """Авторизация пользователя"""
    credentials = get_user_credentials(username)
    if not credentials:
        return False
    
    password_real, salt = credentials
    hash_password_check = hash_password(password, salt)
    
    if password_real == hash_password_check:
        return update_user_last_seen(user_id, username)
    return False

def reg_user_first_check(user_id):
    """Проверка существования пользователя"""
    return check_user_exists(user_id)

def create_table(user_id):
    """Создание таблицы с информацией о пользователе"""
    user_info = get_user_info(user_id)
    if not user_info:
        return "Зарегистрируйтесь в аккаунт на этом устройстве!\n\n*Одновременный вход с нескольких аккаунтов Telegram невозможен!"
    
    username, status, balance = user_info
    return f"""
    <b>АККАУНТ</b>

👾<b>Имя</b>👾: {username};
#####
👑<b>Статус</b>👑: {status};
#####
💵💶<b>Баланc</b>💷💴: {balance};
#####
<i>Тех. поддержка: sker.msmk@gmail.com</i>"""

def delete_account(user_id):
    """Удаление аккаунта"""
    return delete_user(user_id)

# Инициализация баз данных при импорте
initialize_databases()