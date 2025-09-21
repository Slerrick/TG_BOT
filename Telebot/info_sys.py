import psutil

def check_cpu():
    """Проверка загрузки CPU"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        
        print(f"Загрузка CPU: {cpu_percent}%")
        print(f"Загрузка ядер: {cpu_per_core}")
        
    except Exception as e:
        print(f"Ошибка при проверке CPU: {e}")

def check_disk(path="C:"):
    """Проверка использования диска"""
    try:
        disk_usage = psutil.disk_usage(path)
        
        print(f"Использование диска {path}: {disk_usage.percent}%")
        print(f"Свободно: {disk_usage.free / (1024**3):.2f} GB")
        
    except Exception as e:
        print(f"Ошибка при проверке диска: {e}")

def check_memory():
    """Проверка использования памяти"""
    try:
        memory = psutil.virtual_memory()
        
        print(f"Использование памяти: {memory.percent}%")
        print(f"Доступно: {memory.available / (1024**3):.2f} GB")
        
    except Exception as e:
        print(f"Ошибка при проверке памяти: {e}")

def complex_check():
    """Комплексная проверка системы"""
    check_cpu()
    check_disk()
    check_memory()