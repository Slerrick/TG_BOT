from telebot import types as ty
from Telebot.Parts.keyboardfunction import FIB_TEXT
from service import payment
from handlers import register_user
import Telebot.database as sqlite
from main import BOT

@BOT.callback_query_handler(func=lambda call: True)
def handle_callback(call: ty.CallbackQuery):
    """Обработчик callback запросов"""
    message = call.message
    user_id = message.from_user.id
    
    try:
        if call.data == "fib":
            BOT.send_message(message.chat.id, FIB_TEXT)
            BOT.answer_callback_query(call.id, text="Запрос принят.")
        
        elif call.data == "reg":
            if sqlite.reg_user_first_check(message):
                BOT.send_message(
                    message.chat.id, 
                    "Вы уже зарегистрированы. Если не можете войти в аккаунт, его можно удалить и создать новый."
                )
            else:
                BOT.send_message(message.chat.id, "Введите имя пользователя:")
                BOT.register_next_step_handler(
                    message, 
                    lambda msg: register_user(msg, user_id)
                )
            BOT.answer_callback_query(call.id, text="Запрос принят.")
        
        elif call.data == "enter":
            BOT.send_message(message.chat.id, "Введи одним сообщением имя, а потом через пробел пароль.")
            BOT.register_next_step_handler(
                message, 
                lambda msg: sqlite.enter_user(msg, user_id)
            )
            BOT.answer_callback_query(call.id, text="Запрос принят.")
        
        elif call.data == "del":
            BOT.send_message(message.chat.id, "Напишите ДА/НЕТ, если хотите удалить/оставить аккаунт.")
            BOT.register_next_step_handler(
                message, 
                lambda msg: sqlite.delete_account(msg, user_id)
            )
            BOT.answer_callback_query(call.id, text="Запрос принят.")
        
        elif call.data == "info":
            user_info = sqlite.create_table(message, user_id)
            BOT.send_message(message.chat.id, user_info, parse_mode="html")
            BOT.answer_callback_query(call.id)
        
        elif call.data.startswith("pay_"):
            # Обработка запроса на оплату
            try:
                amount = int(call.data.split("_")[1])
                payment(message, amount)
            except (ValueError, IndexError):
                BOT.send_message(message.chat.id, "Ошибка обработки платежа.")
            BOT.answer_callback_query(call.id)
        
        elif call.data == "cancel_payment":
            BOT.send_message(message.chat.id, "Оплата отменена.")
            BOT.answer_callback_query(call.id)
    except Exception as e:
        print(f"Ошибка обработки callback: {e}")
        BOT.answer_callback_query(call.id, text="Произошла ошибка")