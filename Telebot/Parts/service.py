import time
from datetime import datetime
from telebot import types
from Parts.configserver import PAYMENT_TOKEN
from database import clear_admins_db, delete_inactive_accounts_db, check_admins_db
from info_sys import complex_check

# Глобальная переменная для хранения информации о платежах
payment_sessions = {}

def check_time():
    """Проверка времени для автоматических задач"""
    while True:
        try:
            current_time = datetime.now()
            if current_time.hour == 23 and current_time.minute == 39:
                clear_admins_db()
                delete_inactive_accounts_db()
                print("Выполнена очистка неактивных данных")
                time.sleep(60)
            else:
                time.sleep(20)
                complex_check()
        except Exception as e:
            print(f"Ошибка в фоновом потоке: {e}")
            time.sleep(60)

def check_admins(user_id):
    """Проверка прав администратора"""
    return check_admins_db(user_id)

def send_zip_file(chat_id, zip_path="./javascript-snakes-master.zip"):
    """Отправка ZIP файла"""
    from main import bot
    try:
        with open(zip_path, "rb") as zip_file:
            bot.send_document(chat_id, zip_file, caption="Вот ваш ZIP-архив!")
    except FileNotFoundError:
        bot.send_message(chat_id, "Файл не найден. Повторите попытку позже.")
    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
        bot.send_message(chat_id, "Ошибка при отправке файла.")

def payment(message, amount):
    """Обработка платежа звездами"""
    from main import bot
    try:
        # Сохраняем информацию о платеже
        payment_sessions[message.chat.id] = {
            'amount': amount,
            'user_id': message.from_user.id,
            'timestamp': datetime.now()
        }
        
        bot.send_invoice(
            chat_id=message.chat.id,
            title="Пополнение баланса SKM",
            description=f"Пополнение баланса на {amount} SKM",
            invoice_payload=f"skm_topup_{amount}_{message.from_user.id}",
            provider_token=PAYMENT_TOKEN,
            currency="XTR",
            prices=[types.LabeledPrice(label=f"{amount} SKM", amount=amount * 100)],
            photo_url="https://img.icons8.com/color/96/000000/star--v1.png",
            photo_size=100,
            photo_width=100,
            photo_height=100,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
    except Exception as e:
        print(f"Ошибка при создании платежа: {e}")
        bot.send_message(message.chat.id, "Ошибка при создании платежа. Попробуйте позже.")

def cleanup_payment_sessions():
    """Очистка устаревших платежных сессий"""
    while True:
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for chat_id, session_data in payment_sessions.items():
                if (current_time - session_data['timestamp']).total_seconds() > 3600:
                    expired_sessions.append(chat_id)
            
            for chat_id in expired_sessions:
                del payment_sessions[chat_id]
                
            time.sleep(3600)
            
        except Exception as e:
            print(f"Ошибка при очистке платежных сессий: {e}")
            time.sleep(600)