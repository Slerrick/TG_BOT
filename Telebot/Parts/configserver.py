BOT_TOKEN = "7399585156:AAHKGQhjwaoIDbabDd1nW5eVSrAilfRlvUg"
ADMIN_KEY = "8auy"
PAYMENT_TOKEN = ""

# Текстовые константы
HELLO_TEXT = """
Твой единомышленник в мире программирования!
Этот бот постарается помочь разобраться начальном освоении программирования   :) 
•📚Полезные статьи: Изучай статьи на актуальные темы (Type/Java Script; Python).
•💡Проекты: Узнай о проектах и почерпни вдохновение для собственных, помогай решать проблемы и исправляй свои!
•🛒Магазин: Покупай SKM для внутренних товаров..."""

FIB_TEXT = """import timeit
def fibonacci_iterative(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return 0

# Измеряем время выполнения итеративной функции
elapsed_time_iterative = timeit.timeit(lambda: fibonacci_iterative(1_500_000), number=1)
print(f"Время выполнения: {elapsed_time_iterative:.2f} секунд")
f = input()

Скопируй код и проверь, за какое время твой пк сможет пересчитать по порядку полторамиллиона раз последовательность Фибоначчи!"""

LIST_COMMANDS = """
Вот список команд:
1) /user_list
2) /admin_list"""