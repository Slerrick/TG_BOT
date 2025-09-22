import json
from datetime import datetime
from telebot import TeleBot
from telebot import types
from Parts.configserver import HELLO_TEXT, LIST_COMMANDS, FIB_TEXT, FRONTEND, FRONTEND_MARKDOWN, LINUX, LINUX_MARKDOWN, PHOTOSHOP
from Parts.keyboardfunction import (
    get_main_menu_keyboard, get_registration_keyboard, 
    get_shop_keyboard, get_categories_keyboard, 
    get_website_keyboard, get_payment_keyboard
)
from Parts.service import check_admins, payment_sessions
from database import (
    set_user_name, save_info_user, delete_account, 
    set_skm_user, list_users, list_admins, enter_user, 
    reg_user_first_check, create_table, update_user_balance
)

# Глобальная переменная для хранения состояний пользователей
user_states = {}

def register_handlers(bot: TeleBot):
    # Обработчики команд
    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        """Обработчик команды /start"""
        bot.send_message(
            message.chat.id, 
            f"<b>Привет, </b>{message.from_user.first_name}!{HELLO_TEXT}", 
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )

    @bot.message_handler(commands=["web"])
    def cmd_web(message):
        """Обработчик команды /web"""
        bot.send_message(
            message.chat.id, 
            "А вот и мой первый сайт 😊", 
            reply_markup=get_website_keyboard()
        )

    @bot.message_handler(commands=["admin"])
    def cmd_admin(message):
        """Обработчик команды /admin"""
        if check_admins(message.from_user.id):
            bot.send_message(message.chat.id, "Дарова!")
            bot.send_message(message.chat.id, LIST_COMMANDS)
            print("Предоставлены права админа")
        else:
            bot.send_message(message.chat.id, "Не админ!")

    @bot.message_handler(commands=["admin_list"])
    def cmd_admin_list(message):
        """Обработчик команды /admin_list"""
        if check_admins(message.from_user.id):
            admins_list = list_admins()
            bot.send_message(message.chat.id, admins_list)

    @bot.message_handler(commands=["user_list"])
    def cmd_user_list(message):
        """Обработчик команды /user_list"""
        if check_admins(message.from_user.id):
            users_list = list_users()
            bot.send_message(message.chat.id, users_list)

    # Обработчики контента
    @bot.message_handler(content_types=["photo", "document"])
    def handle_media(message):
        """Обработчик медиафайлов"""
        bot.reply_to(message, "Отличный файл! Жаль, что пока я не могу работать с ним(")

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def process_pre_checkout_query(pre_checkout_query):
        """Обработчик pre-checkout запроса"""
        try:
            print(f"PreCheckoutQuery получен: {pre_checkout_query.id}")
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
            print("PreCheckoutQuery обработан успешно")
        except Exception as e:
            print(f"Ошибка в pre_checkout: {e}")
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False, error_message="Произошла ошибка")

    def payment(call: types.CallbackQuery, price, amount):
        """Обработка платежа звездами"""
        try:
            chat_id = call.message.chat.id
            user_id = call.from_user.id
            
            # Сохраняем информацию о платеже (используем amount вместо price)
            payment_sessions[chat_id] = {
                'amount': amount,  # ← исправлено на amount
                'user_id': user_id,
                'timestamp': datetime.now(),
                'price': price  # ← можно сохранить и price для отладки
            }
            
            bot.send_invoice(
                chat_id=chat_id,  # ← исправлено на chat_id из сообщения
                title="Пополнение баланса SKM",
                description=f"Пополнение баланса на {amount} SKM",
                invoice_payload=f"skm_topup_{amount}_{user_id}_{datetime.now().timestamp()}",
                provider_token="",
                currency="XTR",
                prices=[types.LabeledPrice(label="XTR", amount=price)],
                start_parameter='stars-payment'
            )
            print(f"Создание инвойса для chat_id: {chat_id}, amount: {amount}")
        except Exception as e:
            print(f"Ошибка в payment: {e}")
            bot.send_message(call.message.chat.id, "❌ Ошибка при создании платежа")

    @bot.message_handler(content_types=["successful_payment"])
    def handle_successful_payment(message):
        """Обработчик успешного платежа"""
        try:
            chat_id = message.chat.id
            payment_info = payment_sessions.get(chat_id, {})
            
            # Используем amount который сохранили
            amount = payment_info.get('amount', 0)
            user_id = payment_info.get('user_id', message.from_user.id)
            
            print(f"Успешный платеж: chat_id={chat_id}, amount={amount}")
            
            if amount > 0:
                success = set_skm_user(user_id, amount)
                if success:
                    bot.send_message(
                        chat_id, 
                        f"✅ Оплата прошла успешно! На ваш счет зачислено {amount} SKM."
                    )
                    
                    # Очищаем сессию
                    if chat_id in payment_sessions:
                        del payment_sessions[chat_id]
                else:
                    bot.send_message(chat_id, "❌ Не удалось зачислить средства.")
            else:
                bot.send_message(chat_id, "❌ Не удалось определить сумму платежа.")
                
        except Exception as e:
            print(f"Ошибка в successful_payment: {e}")
            bot.send_message(message.chat.id, "❌ Произошла ошибка при обработке платежа")

    @bot.message_handler(content_types=["web_app_data"])
    def handle_web_app_data(message):
        """Обработчик данных из веб-приложения"""
        try:
            res = json.loads(message.web_app_data.data)
            amount = res.get('amount', 0)
            price = res.get('price', 0)
            
            if int(amount) > 0:
                bot.send_message(
                    message.chat.id, 
                    f"Для пополнения баланса на {amount} SKM нажмите кнопку оплаты:",
                    reply_markup=get_payment_keyboard(price, amount)
                )
            else:
                bot.send_message(message.chat.id, "Неверная сумма для пополнения.")
                
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            bot.send_message(message.chat.id, "Ошибка обработки данных")
        except Exception as e:
            print(f"Ошибка обработки web app данных: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
    def handle_purchase(call):
        """Обработчик покупки через callback"""
        try:
            user_id = call.from_user.id
            chat_id = call.message.chat.id
            
            # Извлекаем ID товара из callback данных
            amount = int(call.data.split('_')[1])
            product = call.data.split('_')[2]
            # Проверяем баланс пользователя
            user_balance = update_user_balance(user_id, amount)
        
            if user_balance:

                bot.send_message(chat_id, f"✅ Оплата прошла успешно! {abs(amount)} SKM списано с вашего счета.")
                give_product(chat_id, product)
            else:
                bot.send_message(chat_id, "❌ Ошибка при списании средств.")
            
            bot.answer_callback_query(call.id)

        except Exception as e:
            print(f"Ошибка обработки покупки: {e}")
            bot.answer_callback_query(call.id, "Произошла ошибка")

    def give_product(chat_id, product):
        match product:
            case "photoshop2024":
                bot.send_message(chat_id, PHOTOSHOP)
                bot.send_message(chat_id, "Для корректной работы необходимо скачать все файлы в одну папку и установить adobe creative cloud (бесплатно)")
            case _:
                pass

    # Обработчики текстовых сообщений
    @bot.message_handler(func=lambda message: message.text == "Аккаунт")
    def handle_account(message):
        """Обработчик аккаунта"""
        bot.send_message(message.chat.id, "Действия с аккаунтом:", reply_markup=get_registration_keyboard())

    @bot.message_handler(func=lambda message: message.text == "Назад")
    def handle_back(message):
        """Обработчик кнопки Назад"""
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=get_main_menu_keyboard())

    @bot.message_handler(func=lambda message: message.text == "Магазин SKM")
    def handle_shop(message):
        """Обработчик магазина"""
        bot.send_message(
            message.chat.id, 
            "Нажмите на кнопку, чтобы открыть веб-приложение",
            reply_markup=get_shop_keyboard()
        )

    @bot.message_handler(func=lambda message: message.text == "Категории")
    def handle_categories(message):
        """Обработчик категорий"""
        bot.send_message(message.chat.id, "Ссылки на страницы тем", reply_markup=get_categories_keyboard())

    # Обработчики callback запросов
    @bot.callback_query_handler(func=lambda call: call.data == "fib")
    def handle_fib(call):
        """Обработчик Fibonacci"""
        bot.send_message(call.message.chat.id, FIB_TEXT)
        bot.answer_callback_query(call.id, text="Запрос принят.")

    @bot.callback_query_handler(func=lambda call: call.data == "reg")
    def handle_reg(call):
        """Обработчик регистрации"""
        if reg_user_first_check(call.from_user.id):
            bot.send_message(
                call.message.chat.id, 
                "Вы уже зарегистрированы. Если не можете войти в аккаунт, его можно удалить и создать новый."
            )
        else:
            bot.send_message(call.message.chat.id, "Введите имя пользователя:")
            user_states[call.from_user.id] = {"state": "waiting_for_username"}
        bot.answer_callback_query(call.id, text="Запрос принят.")

    @bot.callback_query_handler(func=lambda call: call.data == "enter")
    def handle_enter(call):
        """Обработчик входа"""
        bot.send_message(call.message.chat.id, "Введи одним сообщением имя, а потом через пробел пароль.")
        user_states[call.from_user.id] = {"state": "waiting_for_login"}
        bot.answer_callback_query(call.id, text="Запрос принят.")

    @bot.callback_query_handler(func=lambda call: call.data == "del")
    def handle_delete(call):
        """Обработчик удаления"""
        bot.send_message(call.message.chat.id, "Напишите ДА/НЕТ, если хотите удалить/оставить аккаунт.")
        user_states[call.from_user.id] = {"state": "waiting_for_delete_confirmation"}
        bot.answer_callback_query(call.id, text="Запрос принят.")

    @bot.callback_query_handler(func=lambda call: call.data == "info")
    def handle_info(call):
        """Обработчик информации"""
        user_info = create_table(call.from_user.id)
        bot.send_message(call.message.chat.id, user_info, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
    def handle_pay(call: types.CallbackQuery):
        """Обработчик оплаты"""
        try:
            price = int(call.data.split("_")[1])
            amount = int(call.data.split("_")[2])
            payment(call, price, amount)
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "Ошибка обработки платежа.")
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_payment")
    def handle_cancel_payment(call):
        """Обработчик отмены оплаты"""
        bot.send_message(call.message.chat.id, "Оплата отменена.")
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "prog")
    def handle_hardware(call):
        bot.send_message(call.message.chat.id, LINUX)
        bot.send_message(call.message.chat.id, LINUX_MARKDOWN)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "learnfrontend")
    def handle_hardware(call):
        bot.send_message(call.message.chat.id, FRONTEND)
        bot.send_message(call.message.chat.id, FRONTEND_MARKDOWN)
        bot.answer_callback_query(call.id)
        

    # Обработчики состояний
    @bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "waiting_for_username")
    def process_username(message):
        """Обработка имени пользователя"""
        set_user_name(message.text.strip())
        bot.send_message(message.chat.id, "Придумайте пароль:")
        user_states[message.from_user.id] = {"state": "waiting_for_password"}

    @bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "waiting_for_password")
    def process_password(message):
        """Обработка пароля"""
        success = save_info_user(message.from_user.id, message.text.strip())
        if success:
            bot.send_message(message.chat.id, "Регистрация окончена")
        else:
            bot.send_message(message.chat.id, "Ошибка регистрации. Возможно, имя уже занято.")
        user_states.pop(message.from_user.id, None)

    @bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "waiting_for_login")
    def process_login(message):
        """Обработка входа"""
        try:
            parts = message.text.split()
            if len(parts) >= 2:
                username, password = parts[0], parts[1]
                if enter_user(username, password, message.from_user.id):
                    user_info = create_table(message.from_user.id)
                    bot.send_message(message.chat.id, user_info, parse_mode="HTML")
                else:
                    bot.send_message(message.chat.id, "Неверные данные для входа.")
            else:
                bot.send_message(message.chat.id, "Пожалуйста, введите имя и пароль через пробел.")
        except Exception as e:
            bot.send_message(message.chat.id, "Ошибка при входе.")
        user_states.pop(message.from_user.id, None)

    @bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get("state") == "waiting_for_delete_confirmation")
    def process_delete_confirmation(message):
        """Обработка подтверждения удаления"""
        if message.text.upper() == "ДА":
            success = delete_account(message.from_user.id)
            if success:
                bot.send_message(message.chat.id, "Аккаунт удален!")
            else:
                bot.send_message(message.chat.id, "Ошибка при удалении аккаунта.")
        else:
            bot.send_message(message.chat.id, "Отмена операции.")
        user_states.pop(message.from_user.id, None)