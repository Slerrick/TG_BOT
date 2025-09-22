from telebot import types

def get_main_menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(
        types.KeyboardButton("Категории"),
        types.KeyboardButton("Аккаунт")
    )
    keyboard.add(types.KeyboardButton("Магазин SKM"))
    return keyboard

def get_back_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Назад"))
    return keyboard

def get_registration_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Войти", callback_data="enter"),
        types.InlineKeyboardButton("Зарегистрироваться", callback_data="reg")
    )
    keyboard.add(types.InlineKeyboardButton("Удалить аккаунт", callback_data="del"))
    keyboard.add(types.InlineKeyboardButton("Мои данные", callback_data="info"))
    return keyboard

def get_shop_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(
        text="Открыть веб-приложение",
        web_app=types.WebAppInfo(url="https://slerrick.github.io/TG_BOT/")
    ))
    keyboard.add(types.KeyboardButton("Назад"))
    return keyboard

def get_categories_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Программы Linux", callback_data="prog"),
        types.InlineKeyboardButton("Материалы Frontend", callback_data="learnfrontend")
    )
    keyboard.add(
        types.InlineKeyboardButton("PhotoShop2024 (1000 SKM)", callback_data="buy_-1000_photoshop2024")
    )
    return keyboard

def get_website_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton("Перейти на сайт!", url="https://slerrick.github.io/WebSite3/"),
        types.InlineKeyboardButton("На всякий случай...", callback_data="fib")
    )
    return keyboard

def get_payment_keyboard(price, amount):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(f"Оплатить {price} звезд", callback_data=f"pay_{price}_{amount}"),
        types.InlineKeyboardButton("Отмена", callback_data="cancel_payment")
    )
    return keyboard