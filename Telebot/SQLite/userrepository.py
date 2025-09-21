from typing import List, Tuple, Optional
from SQLite.databasemanager import DatabaseManager, sqlite3
from datetime import date

# Глобальные переменные (оставлены для совместимости)
name_user: Optional[str] = None
column_count_users: int = 0
column_count_admins: int = 0
info_admins_id: List[Tuple[int]] = []
session_id_admins: List[int] = []

def initialize_databases():
    """Инициализация баз данных"""
    global column_count_users, column_count_admins, info_admins_id
    
    # База пользователей
    try:
        with DatabaseManager("./DATA.DB") as cursor:
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
            
            cursor.execute("SELECT COUNT(*) FROM users")
            column_count_users = cursor.fetchone()[0]
            print(f"Количество пользователей: {column_count_users}")
            
    except Exception as e:
        print(f"Ошибка при инициализации базы пользователей: {e}")
    
    # База администраторов
    try:
        with DatabaseManager("./DATA_ADMIN.DB") as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER UNIQUE NOT NULL
                )''')
            
            cursor.execute("SELECT COUNT(*) FROM admins")
            column_count_admins = cursor.fetchone()[0]
            
            cursor.execute("SELECT chat_id FROM admins")
            info_admins_id = cursor.fetchall()
            
    except Exception as e:
        print(f"Ошибка при инициализации базы администраторов: {e}")
    
    print(f"Количество админов: {column_count_admins}")

def set_user_name(name: str):
    """Установка имени пользователя"""
    global name_user
    name_user = name

def add_admin(user_id: int) -> bool:
    """Добавление администратора"""
    global column_count_admins, session_id_admins
    try:
        with DatabaseManager("./DATA_ADMIN.DB") as cursor:
            cursor.execute("INSERT OR IGNORE INTO admins (chat_id) VALUES (?)", (user_id,))
            column_count_admins += 1
            session_id_admins.append(user_id)
            print(f"Кто-то вошел как админ, сейчас их {column_count_admins}")
            return True
    except Exception as e:
        print(f"Ошибка при добавлении админа: {e}")
        return False

def add_user(user_id: int, username: str, hashed_password: str, salt: str) -> bool:
    """Добавление пользователя"""
    global column_count_users
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute(
                "INSERT INTO users (id, name, password, salt, lastseen) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, hashed_password, salt, date.today())
            )
            column_count_users += 1
            print(f"Новый пользователь зарегистрировался! Всего: {column_count_users}")
            return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Ошибка при регистрации пользователя: {e}")
        return False

def delete_user(user_id: int) -> bool:
    """Удаление пользователя"""
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return True
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
        return False

def update_user_balance(user_id: int, amount: int) -> bool:
    """Обновление баланса пользователя"""
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?",
                (amount, user_id)
            )
            return True
    except Exception as e:
        print(f"Ошибка при обновлении баланса: {e}")
        return False

def get_user_credentials(username: str) -> Optional[Tuple[str, str]]:
    """Получение учетных данных пользователя"""
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute("SELECT password, salt FROM users WHERE name = ?", (username,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении учетных данных: {e}")
        return None

def update_user_last_seen(user_id: int, username: str) -> bool:
    """Обновление времени последнего входа"""
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute(
                "UPDATE users SET lastseen = ?, id = ? WHERE name = ?",
                (date.today(), user_id, username)
            )
            return True
    except Exception as e:
        print(f"Ошибка при обновлении последнего входа: {e}")
        return False

def get_user_info(user_id: int) -> Optional[Tuple[str, str, int]]:
    """Получение информации о пользователе"""
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute(
                "SELECT name, status, balance FROM users WHERE id = ?",
                (user_id,)
            )
            return cursor.fetchone()
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return None

def check_user_exists(user_id: int) -> bool:
    """Проверка существования пользователя"""
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке пользователя: {e}")
        return False

def get_all_users() -> List[Tuple]:
    """Получение всех пользователей"""
    try:
        with DatabaseManager("./DATA.DB") as cursor:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка пользователей: {e}")
        return []

def get_all_admins() -> List[Tuple]:
    """Получение всех администраторов"""
    try:
        with DatabaseManager("./DATA_ADMIN.DB") as cursor:
            cursor.execute("SELECT * FROM admins")
            return cursor.fetchall()
    except Exception as e:
        print(f"Ошибка при получении списка администраторов: {e}")
        return []

def add_admins_to_session() -> List[int]:
    """Добавление администраторов в сессию"""
    session_admins = []
    for numbers in info_admins_id:
        for number in numbers:
            session_admins.append(int(number))
    return session_admins

# Инициализация баз данных
initialize_databases()
session_id_admins = add_admins_to_session()