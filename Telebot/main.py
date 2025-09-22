import threading
from telebot import TeleBot
from Parts.configserver import BOT_TOKEN
from Parts.handlers import register_handlers
from Parts.service import check_time, cleanup_payment_sessions

# Инициализация бота
bot = TeleBot(BOT_TOKEN)

# Регистрация обработчиков
register_handlers(bot)

if __name__ == "__main__":
    # Запуск фоновых задач
    background_thread = threading.Thread(target=check_time, daemon=True)
    background_thread.start()
    
    cleanup_thread = threading.Thread(target=cleanup_payment_sessions, daemon=True)
    cleanup_thread.start()
    
    print("Бот запущен...")
    bot.infinity_polling(none_stop=True)