from SQLite.databasemanager import hash_password, generate_salt
from SQLite.userrepository import (
    add_admin, add_user, delete_user, update_user_balance,
    get_user_credentials, update_user_last_seen, get_user_info,
    check_user_exists, get_all_users, get_all_admins,
    name_user, session_id_admins
)
from Telebot.Parts.keyboardfunction import ADMIN_KEY, back_button
from Telebot.Parts.keyboardfunction import BOT

def save_info_user(message, additional_arg: int):
    """Сохранение информации о пользователе"""
    password_user = message.text.strip()
    
    if len(password_user) >= 30:
        BOT.send_message(message.chat.id, "Пароль слишком длинный, повторите попытку")
        return
    
    # Проверка на администратора
    if name_user == "ADMIN" and password_user == ADMIN_KEY:
        if add_admin(message.chat.id):
            BOT.send_message(message.chat.id, "Вы вошли как админ")
            BOT.send_message(message.chat.id, "Регистрация админа окончена")
        return
    
    # Регистрация обычного пользователя
    salt = generate_salt()
    hashed_password = hash_password(password_user, salt)
    
    if add_user(additional_arg, name_user, hashed_password, salt):
        BOT.send_message(message.chat.id, "Регистрация окончена")
    else:
        BOT.send_message(message.chat.id, "Имя занято или аккаунт уже создан.")
    
    back_button(message)

def delete_account(message, additional_arg: int):
    """Удаление аккаунта"""
    if message.text.upper() == "ДА":
        if delete_user(additional_arg):
            BOT.send_message(message.chat.id, "Аккаунт удален!")
            print("Удаление завершено!")
        else:
            BOT.send_message(message.chat.id, "Ошибка при удалении аккаунта")
    else:
        BOT.send_message(message.chat.id, "Отмена операции.")

def set_skm_user(message, amount: int, user_id: int):
    """Пополнение баланса пользователя"""
    if update_user_balance(user_id, amount):
        user_info = get_user_info(user_id)
        if user_info is None:
            BOT.send_message(message.chat.id, "Для пополнения баланса нужно зарегистрироваться!")
        else:
            BOT.send_message(message.chat.id, "Успешно!")
    else:
        BOT.send_message(message.chat.id, "Ошибка при пополнении баланса")

def list_users() -> str:
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

def list_admins() -> str:
    """Получение списка администраторов"""
    admins = get_all_admins()
    if not admins:
        return "Администраторы не найдены"
    
    info_lines = []
    for admin in admins:
        info_lines.append(f"ID:{admin[0]}\nKey:{admin[1]}\n")
    
    return "\n".join(info_lines)

def enter_user(message, additional_arg: int):
    """Авторизация пользователя"""
    try:
        info_list = message.text.split()
        
        if len(info_list) < 2:
            BOT.send_message(message.chat.id, "Пожалуйста, введите имя и пароль через пробел.")
            return
        
        username, password = info_list[0], info_list[1]
        
        credentials = get_user_credentials(username)
        if not credentials:
            BOT.send_message(message.chat.id, "Пользователь не найден")
            return
        
        password_real, salt = credentials
        hash_password_check = hash_password(password, salt)
        
        if password_real == hash_password_check:
            BOT.send_message(message.chat.id, "Вход выполнен!")
            print("Аутентификация прошла успешно!")
            
            if update_user_last_seen(additional_arg, username):
                BOT.send_message(message.chat.id, create_table(message, additional_arg), parse_mode="html")
            else:
                BOT.send_message(message.chat.id, "Ошибка при обновлении данных")
        else:
            BOT.send_message(message.chat.id, "Неправильный пароль или имя")
            print("Неверный пароль.")
                
    except Exception as e:
        print(f"Ошибка при авторизации: {e}")
        BOT.send_message(message.chat.id, "Ошибка при авторизации")

def reg_user_first_check(message) -> bool:
    """Проверка существования пользователя"""
    return check_user_exists(message.from_user.id)

def create_table(message, user_id: int) -> str:
    """Создание таблицы с информацией о пользователе"""
    user_info = get_user_info(user_id)
    if not user_info:
        return "Зарегистрируйтесь в аккаунт на этом устройстве!\n\n*Одновременный вход с нескольких аккаунтов Telegram невозможен!"
    
    username, status, balance = user_info
    result = UserTable.create_table(username, status, balance)
    back_button(message)
    return result

def check_admins(user_id: int) -> bool:
    """Проверка прав администратора"""
    return user_id in session_id_admins

class UserTable:
    """Класс для создания таблицы пользователя"""
    @staticmethod
    def create_table(username: str, status: str, balance: int) -> str:
        """Создает HTML таблицу с информацией о пользователе"""
        return f"""
        <b>АККАУНТ</b>

👾<b>Имя</b>👾: {username};
#####
👑<b>Статус</b>👑: {status};
#####
💵💶<b>Баланc</b>💷💴: {balance};
#####
<i>Тех. поддержка: sker.msmk@gmail.com</i>"""